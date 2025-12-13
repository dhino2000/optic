"""
Predictor for ROI classifier.
Handles inference on new data and integration with DataManager.
"""
from __future__ import annotations
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

from ..utils.model_io import loadModel
from ..data.preprocessing import preprocessTraceForModel


class RoiClassifierPredictor:
    """
    Predictor class for ROI classification.
    
    Loads a trained model and provides methods for predicting
    cell types from trace data.
    """
    
    def __init__(
            self,
            model_path: str,
            device: Optional[torch.device] = None,
        ):
        """
        Initialize the predictor.
        
        Args:
            model_path: Path to saved model file
            device: Device to run inference on (None = auto-detect)
        """
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.device = device
        self.model_path = model_path
        
        # Load model and metadata
        self.model, self.metadata = loadModel(model_path, device)
        self.model.eval()
        
        # Extract useful info
        self.class_names = self.metadata["class_names"]
        self.n_classes = self.metadata["n_classes"]
        self.preprocessing_config = self.metadata["preprocessing_config"]
        
        # Create index to class name mapping
        self.idx_to_class = {i: name for i, name in enumerate(self.class_names)}
    
    def predictSingleTrace(
            self,
            f_trace: np.ndarray,
            fneu_trace: np.ndarray,
        ) -> Tuple[str, np.ndarray]:
        """
        Predict cell type for a single trace.
        
        Args:
            f_trace: F trace (n_frames,)
            fneu_trace: Fneu trace (n_frames,)
        
        Returns:
            Tuple of (predicted_class_name, class_probabilities)
        """
        # Preprocess
        processed = preprocessTraceForModel(
            f_trace=f_trace,
            fneu_trace=fneu_trace,
            fneu_coefficient=self.preprocessing_config.get("fneu_coefficient", 0.7),
            baseline_percentile=self.preprocessing_config.get("baseline_percentile", 10.0),
            normalize_method=self.preprocessing_config.get("normalize_method"),
        )
        
        # Convert to tensor: (1, 1, n_frames)
        trace_tensor = torch.from_numpy(processed.astype(np.float32))
        trace_tensor = trace_tensor.unsqueeze(0).unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(trace_tensor)
            proba = torch.softmax(outputs, dim=1)
            pred_idx = torch.argmax(proba, dim=1).item()
        
        pred_class = self.idx_to_class[pred_idx]
        proba_np = proba.cpu().numpy()[0]
        
        return pred_class, proba_np
    
    def predictBatch(
            self,
            f_traces: np.ndarray,
            fneu_traces: np.ndarray,
        ) -> Tuple[List[str], np.ndarray]:
        """
        Predict cell types for multiple traces.
        
        Args:
            f_traces: F traces (n_rois, n_frames)
            fneu_traces: Fneu traces (n_rois, n_frames)
        
        Returns:
            Tuple of (list of predicted class names, probabilities array (n_rois, n_classes))
        """
        n_rois = f_traces.shape[0]
        
        # Preprocess all traces
        processed_traces = []
        for i in range(n_rois):
            processed = preprocessTraceForModel(
                f_trace=f_traces[i],
                fneu_trace=fneu_traces[i],
                fneu_coefficient=self.preprocessing_config.get("fneu_coefficient", 0.7),
                baseline_percentile=self.preprocessing_config.get("baseline_percentile", 10.0),
                normalize_method=self.preprocessing_config.get("normalize_method"),
            )
            processed_traces.append(processed.astype(np.float32))
        
        # Pad to same length
        max_len = max(t.shape[0] for t in processed_traces)
        padded_traces = np.zeros((n_rois, 1, max_len), dtype=np.float32)
        for i, trace in enumerate(processed_traces):
            padded_traces[i, 0, :trace.shape[0]] = trace
        
        # Convert to tensor
        traces_tensor = torch.from_numpy(padded_traces).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(traces_tensor)
            proba = torch.softmax(outputs, dim=1)
            pred_indices = torch.argmax(proba, dim=1)
        
        # Convert to class names
        pred_classes = [self.idx_to_class[idx.item()] for idx in pred_indices]
        proba_np = proba.cpu().numpy()
        
        return pred_classes, proba_np
    
    def predictFromFallDict(
            self,
            dict_fall: Dict[str, Any],
        ) -> Tuple[List[str], np.ndarray, Dict[int, str]]:
        """
        Predict cell types from Fall.mat dictionary.
        
        Args:
            dict_fall: Dictionary loaded from Fall.mat
        
        Returns:
            Tuple of:
            - List of predicted class names
            - Probabilities array (n_rois, n_classes)
            - Dictionary mapping ROI ID to predicted class name
        """
        f_traces = dict_fall["F"]
        fneu_traces = dict_fall["Fneu"]
        
        pred_classes, proba = self.predictBatch(f_traces, fneu_traces)
        
        # Build ROI ID to class mapping
        roi_to_class = {i: pred_class for i, pred_class in enumerate(pred_classes)}
        
        return pred_classes, proba, roi_to_class
    
    def getModelInfo(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_path": self.model_path,
            "model_type": self.metadata["model_config"]["model_type"],
            "class_names": self.class_names,
            "n_classes": self.n_classes,
            "final_accuracy": self.metadata.get("final_accuracy"),
            "created_at": self.metadata.get("created_at"),
        }


def predictAndUpdateDataManager(
        predictor: RoiClassifierPredictor,
        data_manager,
        app_key: str,
    ) -> Dict[int, str]:
    """
    Predict cell types and update DataManager.
    
    This function is designed for integration with Suite2pROICurationGUI.
    
    Args:
        predictor: RoiClassifierPredictor instance
        data_manager: DataManager instance from optic
        app_key: Application key (e.g., "pri")
    
    Returns:
        Dictionary mapping ROI ID to predicted class name
    """
    # Get traces from DataManager
    dict_fall = data_manager.getDictFall(app_key)
    
    # Predict
    pred_classes, proba, roi_to_class = predictor.predictFromFallDict(dict_fall)
    
    return roi_to_class


def buildCelltypeArraysFromPredictions(
        predictions: Dict[int, str],
        class_names: List[str],
        n_rois: int,
    ) -> Dict[str, np.ndarray]:
    """
    Build celltype arrays in ROICuration.mat format from predictions.
    
    The ROICuration.mat format stores each celltype as an array of ROI IDs
    that belong to that celltype.
    
    Args:
        predictions: Dictionary mapping ROI ID to class name
        class_names: List of class names
        n_rois: Total number of ROIs
    
    Returns:
        Dictionary mapping class name to array of ROI IDs
    """
    celltype_arrays = {name: [] for name in class_names}
    
    for roi_id in range(n_rois):
        if roi_id in predictions:
            pred_class = predictions[roi_id]
            if pred_class in celltype_arrays:
                celltype_arrays[pred_class].append(roi_id)
    
    # Convert to numpy arrays
    for name in celltype_arrays:
        celltype_arrays[name] = np.array(celltype_arrays[name], dtype=np.int32)
    
    return celltype_arrays