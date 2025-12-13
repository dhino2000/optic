"""
Model I/O utilities for ROI classifier.
Handles saving and loading trained models with their configurations.
"""
from __future__ import annotations
import torch
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Type
from datetime import datetime


# Default save directory
DEFAULT_MODEL_DIR = Path(__file__).parent.parent.parent.parent / "models" / "roi_classifier"


def getDefaultModelDir() -> Path:
    """Get default directory for saving models."""
    return DEFAULT_MODEL_DIR


def ensureModelDir(path: Optional[str] = None) -> Path:
    """
    Ensure model directory exists.
    
    Args:
        path: Optional custom path. If None, uses default.
    
    Returns:
        Path to model directory
    """
    if path is None:
        model_dir = DEFAULT_MODEL_DIR
    else:
        model_dir = Path(path)
    
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir


def saveModel(
        model: torch.nn.Module,
        path: str,
        class_names: list,
        preprocessing_config: Dict[str, Any],
        training_config: Dict[str, Any],
        training_history: Optional[Dict[str, Any]] = None,
        final_accuracy: Optional[float] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> str:
    """
    Save trained model with all configurations.
    
    Args:
        model: Trained PyTorch model
        path: Path to save the model
        class_names: List of class names
        preprocessing_config: Preprocessing configuration dict
        training_config: Training configuration dict
        training_history: Optional training history dict
        final_accuracy: Optional final validation accuracy
        additional_info: Optional additional information to save
    
    Returns:
        Path to saved model file
    """
    # Get model configuration
    model_config = model.getModelConfig()
    
    # Build save dict
    save_dict = {
        # Model
        "model_state_dict": model.state_dict(),
        "model_config": model_config,
        
        # Class information
        "class_names": class_names,
        "n_classes": len(class_names),
        
        # Configurations
        "preprocessing_config": preprocessing_config,
        "training_config": training_config,
        
        # Metadata
        "created_at": datetime.now().isoformat(),
        "pytorch_version": torch.__version__,
    }
    
    # Optional fields
    if training_history is not None:
        save_dict["training_history"] = training_history
    
    if final_accuracy is not None:
        save_dict["final_accuracy"] = final_accuracy
    
    if additional_info is not None:
        save_dict["additional_info"] = additional_info
    
    # Ensure directory exists
    save_path = Path(path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save
    torch.save(save_dict, save_path)
    
    return str(save_path)


def loadModel(
        path: str,
        device: Optional[torch.device] = None,
    ) -> Tuple[torch.nn.Module, Dict[str, Any]]:
    """
    Load trained model from file.
    
    Args:
        path: Path to model file
        device: Device to load model to (None = auto-detect)
    
    Returns:
        Tuple of (model, metadata_dict)
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load checkpoint
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    
    # Get model config
    model_config = checkpoint["model_config"]
    model_type = model_config["model_type"]
    
    # Create model instance
    model = createModelFromConfig(model_config)
    
    # Load state dict
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    
    # Build metadata dict
    metadata = {
        "class_names": checkpoint["class_names"],
        "n_classes": checkpoint["n_classes"],
        "preprocessing_config": checkpoint["preprocessing_config"],
        "training_config": checkpoint["training_config"],
        "model_config": model_config,
        "created_at": checkpoint.get("created_at"),
        "pytorch_version": checkpoint.get("pytorch_version"),
        "final_accuracy": checkpoint.get("final_accuracy"),
        "training_history": checkpoint.get("training_history"),
        "additional_info": checkpoint.get("additional_info"),
    }
    
    return model, metadata


def createModelFromConfig(model_config: Dict[str, Any]) -> torch.nn.Module:
    """
    Create model instance from configuration dictionary.
    
    Args:
        model_config: Model configuration dictionary
    
    Returns:
        Model instance (not loaded with weights)
    """
    model_type = model_config["model_type"]
    
    # Import model classes
    from ..models.cnn_model import CnnClassifier, CnnClassifierWithAttention
    from ..models.rnn_model import RnnClassifier, GruClassifier
    
    # Model registry
    model_registry = {
        "CnnClassifier": CnnClassifier,
        "CnnClassifierWithAttention": CnnClassifierWithAttention,
        "RnnClassifier": RnnClassifier,
        "GruClassifier": GruClassifier,
    }
    
    if model_type not in model_registry:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model_class = model_registry[model_type]
    
    # Build constructor arguments based on model type
    if model_type == "CnnClassifier":
        model = model_class(
            input_channels=model_config["input_channels"],
            n_classes=model_config["n_classes"],
            cnn_channels=model_config.get("cnn_channels"),
            kernel_size=model_config.get("kernel_size", 7),
            dropout=model_config.get("dropout", 0.3),
        )
    elif model_type == "CnnClassifierWithAttention":
        model = model_class(
            input_channels=model_config["input_channels"],
            n_classes=model_config["n_classes"],
            cnn_channels=model_config.get("cnn_channels"),
            kernel_size=model_config.get("kernel_size", 7),
            dropout=model_config.get("dropout", 0.3),
            attention_heads=model_config.get("attention_heads", 4),
        )
    elif model_type in ["RnnClassifier", "GruClassifier"]:
        model = model_class(
            input_channels=model_config["input_channels"],
            n_classes=model_config["n_classes"],
            hidden_size=model_config.get("hidden_size", 128),
            num_layers=model_config.get("num_layers", 2),
            dropout=model_config.get("dropout", 0.3),
            bidirectional=model_config.get("bidirectional", True),
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return model


def getModelInfo(path: str) -> Dict[str, Any]:
    """
    Get model information without fully loading the model.
    
    Args:
        path: Path to model file
    
    Returns:
        Dictionary containing model information
    """
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    
    return {
        "model_type": checkpoint["model_config"]["model_type"],
        "class_names": checkpoint["class_names"],
        "n_classes": checkpoint["n_classes"],
        "final_accuracy": checkpoint.get("final_accuracy"),
        "created_at": checkpoint.get("created_at"),
        "preprocessing_config": checkpoint["preprocessing_config"],
    }


def listSavedModels(directory: Optional[str] = None) -> list:
    """
    List all saved models in directory.
    
    Args:
        directory: Directory to search (None = default)
    
    Returns:
        List of dictionaries with model info
    """
    if directory is None:
        model_dir = DEFAULT_MODEL_DIR
    else:
        model_dir = Path(directory)
    
    if not model_dir.exists():
        return []
    
    models = []
    for path in model_dir.glob("*.pt"):
        try:
            info = getModelInfo(str(path))
            info["path"] = str(path)
            info["filename"] = path.name
            models.append(info)
        except Exception as e:
            # Skip invalid files
            continue
    
    # Sort by creation date (newest first)
    models.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return models


def generateModelFilename(
        class_names: list,
        model_type: str = "cnn",
        suffix: str = "",
    ) -> str:
    """
    Generate a filename for saving model.
    
    Args:
        class_names: List of class names
        model_type: Type of model
        suffix: Optional suffix
    
    Returns:
        Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    classes_str = "_".join(class_names[:3])  # First 3 classes max
    
    if suffix:
        filename = f"roi_classifier_{model_type}_{classes_str}_{timestamp}_{suffix}.pt"
    else:
        filename = f"roi_classifier_{model_type}_{classes_str}_{timestamp}.pt"
    
    return filename