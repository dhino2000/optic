"""
Visualization functions for training history.
Provides non-blocking popup plots compatible with GUI applications.
"""
from __future__ import annotations
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for popup windows
import matplotlib.pyplot as plt
from typing import List, Optional, Dict, Any
import numpy as np


def plotKFoldHistories(
        histories: List[Dict[str, List[float]]],
        val_accuracies: List[float],
        path_save: Optional[str] = None,
        figsize: tuple = (14, 10),
        block: bool = False,
    ) -> plt.Figure:
    """
    Plot training histories for K-fold cross validation.
    
    Args:
        histories: List of TrainingHistory objects or history dictionaries
        val_accuracies: List of final validation accuracies
        figsize: Figure size
        block: If True, blocks execution until window is closed
    
    Returns:
        Matplotlib Figure object
    """
    n_folds = len(histories)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    colors = plt.cm.tab10.colors[:n_folds]
    
    # Plot each fold
    for fold_idx, (history, color) in enumerate(zip(histories, colors)):
        # Handle both TrainingHistory objects and dicts
        if hasattr(history, 'train_losses'):
            # TrainingHistory object
            train_losses = history.train_losses
            val_losses = history.val_losses
            train_accs = history.train_accuracies
            val_accs = history.val_accuracies
        else:
            # Dictionary
            train_losses = history["train_losses"]
            val_losses = history["val_losses"]
            train_accs = history["train_accuracies"]
            val_accs = history["val_accuracies"]
        
        epochs = range(1, len(train_losses) + 1)
        label = f'Fold {fold_idx}'
        
        # Train Loss
        axes[0, 0].plot(epochs, train_losses, color=color, 
                        alpha=0.7, label=label)
        # Val Loss
        axes[0, 1].plot(epochs, val_losses, color=color, 
                        alpha=0.7, label=label)
        # Train Accuracy
        axes[1, 0].plot(epochs, train_accs, color=color, 
                        alpha=0.7, label=label)
        # Val Accuracy
        axes[1, 1].plot(epochs, val_accs, color=color, 
                        alpha=0.7, label=label)
    
    # Configure subplots
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Train Loss')
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].set_title('Validation Loss')
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Accuracy')
    axes[1, 0].set_title('Train Accuracy')
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_ylim([0, 1])
    
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Accuracy')
    axes[1, 1].set_title('Validation Accuracy')
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_ylim([0, 1])
    
    # Add summary text
    mean_acc = np.mean(val_accuracies)
    std_acc = np.std(val_accuracies)
    summary_text = f'Mean Val Acc: {mean_acc:.4f} ± {std_acc:.4f}'
    fig.suptitle(f'K-Fold Training History\n{summary_text}', fontsize=12)
    
    plt.tight_layout()
    if path_save is not None:
        plt.savefig(path_save)
    plt.show(block=block)
    return fig