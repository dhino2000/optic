"""
Trainer for ROI classifier.
Handles training loop, progress reporting, and checkpointing.
"""
from __future__ import annotations
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
import time

from .evaluator import evaluateModel, calculateAccuracy


@dataclass
class TrainingHistory:
    """Container for training history."""
    train_losses: List[float] = field(default_factory=list)
    train_accuracies: List[float] = field(default_factory=list)
    val_losses: List[float] = field(default_factory=list)
    val_accuracies: List[float] = field(default_factory=list)
    
    def append(
            self,
            train_loss: float,
            train_acc: float,
            val_loss: float,
            val_acc: float,
        ) -> None:
        """Append metrics for one epoch."""
        self.train_losses.append(train_loss)
        self.train_accuracies.append(train_acc)
        self.val_losses.append(val_loss)
        self.val_accuracies.append(val_acc)
    
    def toDict(self) -> Dict[str, List[float]]:
        """Convert to dictionary."""
        return {
            "train_losses": self.train_losses,
            "train_accuracies": self.train_accuracies,
            "val_losses": self.val_losses,
            "val_accuracies": self.val_accuracies,
        }


@dataclass
class EpochResult:
    """Result of a single epoch."""
    epoch: int
    train_loss: float
    train_accuracy: float
    val_loss: float
    val_accuracy: float
    elapsed_time: float


class Trainer:
    """
    Trainer class for ROI classifier.
    
    Handles the training loop with:
    - Progress callbacks for GUI integration
    - Checkpoint saving at regular intervals
    - Validation after each epoch
    """
    
    def __init__(
            self,
            model: nn.Module,
            device: torch.device,
            learning_rate: float = 1e-3,
            weight_decay: float = 1e-4,
            class_weights: Optional[torch.Tensor] = None,
        ):
        """
        Initialize the trainer.
        
        Args:
            model: The model to train
            device: Device to train on (cuda or cpu)
            learning_rate: Learning rate for optimizer
            weight_decay: Weight decay for regularization
            class_weights: Optional class weights for imbalanced data
        """
        self.model = model.to(device)
        self.device = device
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        
        # Loss function
        if class_weights is not None:
            class_weights = class_weights.to(device)
        self.criterion = nn.CrossEntropyLoss(weight=class_weights)
        
        # Optimizer
        self.optimizer = Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
        )
        
        # Learning rate scheduler
        self.scheduler = ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.5,
            patience=5,
        )
        
        # Training state
        self.current_epoch = 0
        self.history = TrainingHistory()
        
        # Callbacks
        self.on_epoch_end: Optional[Callable[[EpochResult], None]] = None
        self.on_batch_end: Optional[Callable[[int, int, float], None]] = None
    
    def trainEpoch(
            self, 
            train_loader: DataLoader,
        ) -> Tuple[float, float]:
        """
        Train for one epoch.
        
        Args:
            train_loader: DataLoader for training data
        
        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.train()
        
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        n_batches = len(train_loader)
        
        for batch_idx, (traces, labels, lengths) in enumerate(train_loader):
            traces = traces.to(self.device)
            labels = labels.to(self.device)
            lengths = lengths.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(traces, lengths)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Metrics
            total_loss += loss.item() * labels.size(0)
            predictions = torch.argmax(outputs, dim=1)
            total_correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)
            
            # Batch callback
            if self.on_batch_end is not None:
                self.on_batch_end(batch_idx + 1, n_batches, loss.item())
        
        avg_loss = total_loss / total_samples
        accuracy = total_correct / total_samples
        
        return avg_loss, accuracy
    
    def train(
            self,
            train_loader: DataLoader,
            val_loader: DataLoader,
            n_epochs: int,
            checkpoint_dir: Optional[str] = None,
            checkpoint_interval: int = 10,
        ) -> TrainingHistory:
        """
        Train the model.
        
        Args:
            train_loader: DataLoader for training data
            val_loader: DataLoader for validation data
            n_epochs: Number of epochs to train
            checkpoint_dir: Directory to save checkpoints (None = no checkpoints)
            checkpoint_interval: Save checkpoint every N epochs
        
        Returns:
            TrainingHistory object
        """
        if checkpoint_dir is not None:
            Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
        
        for epoch in range(n_epochs):
            self.current_epoch = epoch + 1
            start_time = time.time()
            
            # Train
            train_loss, train_acc = self.trainEpoch(train_loader)
            
            # Validate
            val_metrics = evaluateModel(
                self.model, val_loader, self.criterion, self.device
            )
            val_loss = val_metrics["loss"]
            val_acc = val_metrics["accuracy"]
            
            # Update learning rate
            self.scheduler.step(val_loss)
            
            # Record history
            self.history.append(train_loss, train_acc, val_loss, val_acc)
            
            elapsed_time = time.time() - start_time
            
            # Epoch callback
            if self.on_epoch_end is not None:
                result = EpochResult(
                    epoch=self.current_epoch,
                    train_loss=train_loss,
                    train_accuracy=train_acc,
                    val_loss=val_loss,
                    val_accuracy=val_acc,
                    elapsed_time=elapsed_time,
                )
                self.on_epoch_end(result)
            
            # Save checkpoint
            if checkpoint_dir is not None and self.current_epoch % checkpoint_interval == 0:
                self.saveCheckpoint(
                    Path(checkpoint_dir) / f"checkpoint_epoch_{self.current_epoch}.pt"
                )
        
        return self.history
    
    def saveCheckpoint(self, path: str) -> None:
        """
        Save training checkpoint.
        
        Args:
            path: Path to save checkpoint
        """
        checkpoint = {
            "epoch": self.current_epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "history": self.history.toDict(),
        }
        torch.save(checkpoint, path)
    
    def loadCheckpoint(self, path: str) -> None:
        """
        Load training checkpoint.
        
        Args:
            path: Path to checkpoint file
        """
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        
        self.current_epoch = checkpoint["epoch"]
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        
        history_dict = checkpoint["history"]
        self.history = TrainingHistory(
            train_losses=history_dict["train_losses"],
            train_accuracies=history_dict["train_accuracies"],
            val_losses=history_dict["val_losses"],
            val_accuracies=history_dict["val_accuracies"],
        )


def trainKFold(
        model_class: type,
        model_kwargs: Dict[str, Any],
        kfold_generator,
        n_epochs: int,
        device: torch.device,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        class_weights: Optional[torch.Tensor] = None,
        checkpoint_dir: Optional[str] = None,
        checkpoint_interval: int = 10,
        on_fold_start: Optional[Callable[[int], None]] = None,
        on_fold_end: Optional[Callable[[int, float], None]] = None,
        on_epoch_end: Optional[Callable[[int, EpochResult], None]] = None,
    ) -> Tuple[List[TrainingHistory], List[float]]:
    """
    Train model with k-fold cross validation.
    
    Args:
        model_class: Model class to instantiate for each fold
        model_kwargs: Keyword arguments for model constructor
        kfold_generator: KFoldDataLoaderGenerator instance
        n_epochs: Number of epochs per fold
        device: Device to train on
        learning_rate: Learning rate
        weight_decay: Weight decay
        class_weights: Optional class weights
        checkpoint_dir: Directory for checkpoints
        checkpoint_interval: Checkpoint interval
        on_fold_start: Callback when fold starts
        on_fold_end: Callback when fold ends (fold_idx, val_accuracy)
        on_epoch_end: Callback when epoch ends (fold_idx, EpochResult)
    
    Returns:
        Tuple of (list of histories, list of validation accuracies)
    """
    all_histories = []
    all_val_accuracies = []
    
    for fold_idx, train_loader, val_loader in kfold_generator:
        # Callback
        if on_fold_start is not None:
            on_fold_start(fold_idx)
        
        # Create new model for this fold
        model = model_class(**model_kwargs)
        
        # Create trainer
        trainer = Trainer(
            model=model,
            device=device,
            learning_rate=learning_rate,
            weight_decay=weight_decay,
            class_weights=class_weights,
        )
        
        # Set epoch callback
        if on_epoch_end is not None:
            trainer.on_epoch_end = lambda result, f=fold_idx: on_epoch_end(f, result)
        
        # Determine checkpoint directory for this fold
        fold_checkpoint_dir = None
        if checkpoint_dir is not None:
            fold_checkpoint_dir = str(Path(checkpoint_dir) / f"fold_{fold_idx}")
        
        # Train
        history = trainer.train(
            train_loader=train_loader,
            val_loader=val_loader,
            n_epochs=n_epochs,
            checkpoint_dir=fold_checkpoint_dir,
            checkpoint_interval=checkpoint_interval,
        )
        
        # Get final validation accuracy
        final_val_acc = history.val_accuracies[-1]
        
        all_histories.append(history)
        all_val_accuracies.append(final_val_acc)
        
        # Callback
        if on_fold_end is not None:
            on_fold_end(fold_idx, final_val_acc)
    
    return all_histories, all_val_accuracies


def trainFinal(
        model: nn.Module,
        train_loader: DataLoader,
        n_epochs: int,
        device: torch.device,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        class_weights: Optional[torch.Tensor] = None,
        checkpoint_dir: Optional[str] = None,
        checkpoint_interval: int = 10,
        on_epoch_end: Optional[Callable[[EpochResult], None]] = None,
    ) -> TrainingHistory:
    """
    Train final model on all data (no validation split).
    
    Args:
        model: Model to train
        train_loader: DataLoader for all training data
        n_epochs: Number of epochs
        device: Device to train on
        learning_rate: Learning rate
        weight_decay: Weight decay
        class_weights: Optional class weights
        checkpoint_dir: Directory for checkpoints
        checkpoint_interval: Checkpoint interval
        on_epoch_end: Callback when epoch ends
    
    Returns:
        TrainingHistory (val metrics will be same as train metrics)
    """
    trainer = Trainer(
        model=model,
        device=device,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        class_weights=class_weights,
    )
    
    if on_epoch_end is not None:
        trainer.on_epoch_end = on_epoch_end
    
    # Use train_loader for both train and val (since we're using all data)
    history = trainer.train(
        train_loader=train_loader,
        val_loader=train_loader,  # Same as train
        n_epochs=n_epochs,
        checkpoint_dir=checkpoint_dir,
        checkpoint_interval=checkpoint_interval,
    )
    
    return history


def printTrainingSummary(
        histories: List[TrainingHistory],
        val_accuracies: List[float],
    ) -> None:
    """
    Print k-fold training summary.
    
    Args:
        histories: List of training histories
        val_accuracies: List of validation accuracies
    """
    print("=" * 50)
    print("K-Fold Training Summary")
    print("=" * 50)
    
    for fold_idx, (history, val_acc) in enumerate(zip(histories, val_accuracies)):
        print(f"Fold {fold_idx}: Val Accuracy = {val_acc:.4f} ({val_acc * 100:.2f}%)")
    
    mean_acc = sum(val_accuracies) / len(val_accuracies)
    std_acc = (sum((acc - mean_acc) ** 2 for acc in val_accuracies) / len(val_accuracies)) ** 0.5
    
    print("-" * 50)
    print(f"Mean Accuracy: {mean_acc:.4f} ({mean_acc * 100:.2f}%)")
    print(f"Std Accuracy:  {std_acc:.4f} ({std_acc * 100:.2f}%)")
    print("=" * 50)