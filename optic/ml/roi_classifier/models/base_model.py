"""
Base model class for ROI classifier.
Defines common interface for all classifier models.
"""
from __future__ import annotations
import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple


class BaseClassifier(nn.Module, ABC):
    """
    Abstract base class for ROI classifiers.
    All classifier models should inherit from this class.
    """
    
    def __init__(
            self,
            input_channels: int = 1,
            n_classes: int = 2,
        ):
        """
        Initialize the base classifier.
        
        Args:
            input_channels: Number of input channels
            n_classes: Number of output classes
        """
        super().__init__()
        self.input_channels = input_channels
        self.n_classes = n_classes
    
    @abstractmethod
    def forward(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, channels, seq_length)
            lengths: Optional tensor of original sequence lengths (batch_size,)
        
        Returns:
            Output tensor of shape (batch_size, n_classes)
        """
        pass
    
    def predict(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Make predictions (class indices).
        
        Args:
            x: Input tensor of shape (batch_size, channels, seq_length)
            lengths: Optional tensor of original sequence lengths
        
        Returns:
            Predicted class indices of shape (batch_size,)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x, lengths)
            predictions = torch.argmax(logits, dim=1)
        return predictions
    
    def predictProba(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Get prediction probabilities.
        
        Args:
            x: Input tensor of shape (batch_size, channels, seq_length)
            lengths: Optional tensor of original sequence lengths
        
        Returns:
            Class probabilities of shape (batch_size, n_classes)
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x, lengths)
            proba = torch.softmax(logits, dim=1)
        return proba
    
    def getModelConfig(self) -> Dict[str, Any]:
        """
        Get model configuration for saving.
        
        Returns:
            Dictionary containing model configuration
        """
        return {
            "model_type": self.__class__.__name__,
            "input_channels": self.input_channels,
            "n_classes": self.n_classes,
        }
    
    def countParameters(self) -> int:
        """
        Count the number of trainable parameters.
        
        Returns:
            Number of trainable parameters
        """
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def printModelSummary(self) -> None:
        """
        Print model summary including architecture and parameter count.
        """
        print("=" * 50)
        print(f"Model: {self.__class__.__name__}")
        print("=" * 50)
        print(f"Input channels: {self.input_channels}")
        print(f"Output classes: {self.n_classes}")
        print(f"Trainable parameters: {self.countParameters():,}")
        print("=" * 50)
        print("Architecture:")
        print(self)
        print("=" * 50)