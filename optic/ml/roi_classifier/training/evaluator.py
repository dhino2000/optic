"""
Evaluator for ROI classifier.
Handles accuracy calculation and model evaluation.
"""
from __future__ import annotations
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple, Optional, Any
import numpy as np


def calculateAccuracy(
        outputs: torch.Tensor, 
        labels: torch.Tensor
    ) -> float:
    """
    Calculate accuracy from model outputs and labels.
    
    Args:
        outputs: Model outputs (logits) of shape (batch_size, n_classes)
        labels: Ground truth labels of shape (batch_size,)
    
    Returns:
        Accuracy as a float between 0 and 1
    """
    predictions = torch.argmax(outputs, dim=1)
    correct = (predictions == labels).sum().item()
    total = labels.size(0)
    return correct / total if total > 0 else 0.0


def evaluateModel(
        model: nn.Module,
        dataloader: DataLoader,
        criterion: nn.Module,
        device: torch.device,
    ) -> Dict[str, float]:
    """
    Evaluate model on a dataset.
    
    Args:
        model: The model to evaluate
        dataloader: DataLoader for evaluation data
        criterion: Loss function
        device: Device to run evaluation on
    
    Returns:
        Dictionary containing 'loss' and 'accuracy'
    """
    model.eval()
    
    total_loss = 0.0
    total_correct = 0
    total_samples = 0
    
    with torch.no_grad():
        for traces, labels, lengths in dataloader:
            traces = traces.to(device)
            labels = labels.to(device)
            lengths = lengths.to(device)
            
            outputs = model(traces, lengths)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item() * labels.size(0)
            predictions = torch.argmax(outputs, dim=1)
            total_correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)
    
    avg_loss = total_loss / total_samples if total_samples > 0 else 0.0
    accuracy = total_correct / total_samples if total_samples > 0 else 0.0
    
    return {
        "loss": avg_loss,
        "accuracy": accuracy,
    }


def getPredictions(
        model: nn.Module,
        dataloader: DataLoader,
        device: torch.device,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get predictions, probabilities, and true labels from model.
    
    Args:
        model: The model to use for predictions
        dataloader: DataLoader for data
        device: Device to run predictions on
    
    Returns:
        Tuple of (predictions, probabilities, true_labels)
        - predictions: (n_samples,) array of predicted class indices
        - probabilities: (n_samples, n_classes) array of class probabilities
        - true_labels: (n_samples,) array of true class indices
    """
    model.eval()
    
    all_predictions = []
    all_probabilities = []
    all_labels = []
    
    with torch.no_grad():
        for traces, labels, lengths in dataloader:
            traces = traces.to(device)
            lengths = lengths.to(device)
            
            outputs = model(traces, lengths)
            probabilities = torch.softmax(outputs, dim=1)
            predictions = torch.argmax(outputs, dim=1)
            
            all_predictions.append(predictions.cpu().numpy())
            all_probabilities.append(probabilities.cpu().numpy())
            all_labels.append(labels.numpy())
    
    return (
        np.concatenate(all_predictions),
        np.concatenate(all_probabilities),
        np.concatenate(all_labels),
    )


def calculateClassAccuracies(
        predictions: np.ndarray,
        true_labels: np.ndarray,
        class_names: List[str],
    ) -> Dict[str, float]:
    """
    Calculate per-class accuracies.
    
    Args:
        predictions: Predicted class indices
        true_labels: True class indices
        class_names: List of class names
    
    Returns:
        Dictionary mapping class name to accuracy
    """
    class_accuracies = {}
    
    for class_idx, class_name in enumerate(class_names):
        mask = true_labels == class_idx
        if mask.sum() > 0:
            correct = (predictions[mask] == true_labels[mask]).sum()
            class_accuracies[class_name] = correct / mask.sum()
        else:
            class_accuracies[class_name] = 0.0
    
    return class_accuracies


def calculateConfusionMatrix(
        predictions: np.ndarray,
        true_labels: np.ndarray,
        n_classes: int,
    ) -> np.ndarray:
    """
    Calculate confusion matrix.
    
    Args:
        predictions: Predicted class indices
        true_labels: True class indices
        n_classes: Number of classes
    
    Returns:
        Confusion matrix of shape (n_classes, n_classes)
        Row = true label, Column = predicted label
    """
    confusion_matrix = np.zeros((n_classes, n_classes), dtype=np.int64)
    
    for true_label, pred_label in zip(true_labels, predictions):
        confusion_matrix[true_label, pred_label] += 1
    
    return confusion_matrix


class EvaluationResult:
    """
    Container for evaluation results.
    """
    
    def __init__(
            self,
            loss: float,
            accuracy: float,
            predictions: np.ndarray,
            probabilities: np.ndarray,
            true_labels: np.ndarray,
            class_names: List[str],
        ):
        """
        Initialize evaluation result.
        
        Args:
            loss: Average loss
            accuracy: Overall accuracy
            predictions: Predicted class indices
            probabilities: Class probabilities
            true_labels: True class indices
            class_names: List of class names
        """
        self.loss = loss
        self.accuracy = accuracy
        self.predictions = predictions
        self.probabilities = probabilities
        self.true_labels = true_labels
        self.class_names = class_names
        
        # Calculate additional metrics
        self.class_accuracies = calculateClassAccuracies(
            predictions, true_labels, class_names
        )
        self.confusion_matrix = calculateConfusionMatrix(
            predictions, true_labels, len(class_names)
        )
    
    def toDict(self) -> Dict[str, Any]:
        """Convert to dictionary for saving."""
        return {
            "loss": self.loss,
            "accuracy": self.accuracy,
            "class_accuracies": self.class_accuracies,
            "confusion_matrix": self.confusion_matrix.tolist(),
        }
    
    def printSummary(self) -> None:
        """Print evaluation summary."""
        print("=" * 50)
        print("Evaluation Results")
        print("=" * 50)
        print(f"Loss: {self.loss:.4f}")
        print(f"Accuracy: {self.accuracy:.4f} ({self.accuracy * 100:.2f}%)")
        print()
        print("Per-class Accuracy:")
        for class_name, acc in self.class_accuracies.items():
            print(f"  {class_name}: {acc:.4f} ({acc * 100:.2f}%)")
        print()
        print("Confusion Matrix:")
        print(f"  Rows: True labels, Columns: Predicted labels")
        print(f"  Classes: {self.class_names}")
        print(self.confusion_matrix)
        print("=" * 50)


def fullEvaluation(
        model: nn.Module,
        dataloader: DataLoader,
        criterion: nn.Module,
        device: torch.device,
        class_names: List[str],
    ) -> EvaluationResult:
    """
    Perform full evaluation of the model.
    
    Args:
        model: The model to evaluate
        dataloader: DataLoader for evaluation data
        criterion: Loss function
        device: Device to run evaluation on
        class_names: List of class names
    
    Returns:
        EvaluationResult object containing all metrics
    """
    # Get basic metrics
    metrics = evaluateModel(model, dataloader, criterion, device)
    
    # Get predictions
    predictions, probabilities, true_labels = getPredictions(
        model, dataloader, device
    )
    
    return EvaluationResult(
        loss=metrics["loss"],
        accuracy=metrics["accuracy"],
        predictions=predictions,
        probabilities=probabilities,
        true_labels=true_labels,
        class_names=class_names,
    )