"""
CNN classifier model for ROI classification.
Uses 1D CNN with Global Average Pooling for variable-length input support.
"""
from __future__ import annotations
import torch
import torch.nn as nn
from typing import Dict, Any, Optional, List

from .base_model import BaseClassifier


class CnnClassifier(BaseClassifier):
    """
    1D CNN classifier with Multi-Statistics Pooling.
    
    Architecture:
        Input (batch, channels, seq_len)
        → [Conv1d → BatchNorm → ReLU → MaxPool] × N layers
        → Multi-Statistics Pooling (mean, max, std, min)
        → Dropout → Linear → Output (batch, n_classes)
    
    Multi-Statistics Pooling extracts multiple statistics from variable-length
    sequences, preserving spike information better than simple GAP.
    """
    
    def __init__(
            self,
            input_channels: int = 1,
            n_classes: int = 2,
            cnn_channels: List[int] = None,
            kernel_size: int = 7,
            dropout: float = 0.3,
            pool_stats: List[str] = None,
        ):
        """
        Initialize the CNN classifier.
        
        Args:
            input_channels: Number of input channels (default: 1 for dF/F0)
            n_classes: Number of output classes
            cnn_channels: List of channel sizes for each conv layer (default: [32, 64, 128])
            kernel_size: Kernel size for conv layers
            dropout: Dropout rate before final linear layer
            pool_stats: List of pooling statistics to use (default: ["mean", "max", "std", "min"])
        """
        super().__init__(input_channels, n_classes)
        
        if cnn_channels is None:
            cnn_channels = [32, 64, 128]
        
        if pool_stats is None:
            pool_stats = ["mean", "max", "std"]  # min excluded (affected by zero padding)
        
        self.cnn_channels = cnn_channels
        self.kernel_size = kernel_size
        self.dropout_rate = dropout
        self.pool_stats = pool_stats
        
        # Build convolutional layers
        self.conv_layers = self._buildConvLayers()
        
        # Classifier head
        # Each stat produces cnn_channels[-1] features
        classifier_input_size = cnn_channels[-1] * len(pool_stats)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(classifier_input_size, n_classes)
    
    def _buildConvLayers(self) -> nn.Sequential:
        """
        Build the convolutional layers.
        
        Returns:
            Sequential module containing all conv layers
        """
        layers = []
        in_channels = self.input_channels
        
        for out_channels in self.cnn_channels:
            layers.extend([
                nn.Conv1d(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    kernel_size=self.kernel_size,
                    padding=self.kernel_size // 2,  # Same padding
                ),
                nn.BatchNorm1d(out_channels),
                nn.ReLU(inplace=True),
                nn.MaxPool1d(kernel_size=2, stride=2),
            ])
            in_channels = out_channels
        
        return nn.Sequential(*layers)
    
    def _multiStatsPool(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Apply multi-statistics pooling.
        
        Args:
            x: Input tensor of shape (batch, channels, seq_len)
            lengths: Original sequence lengths (not used currently)
        
        Returns:
            Pooled tensor of shape (batch, channels * n_stats)
        """
        stats = []
        
        for stat in self.pool_stats:
            if stat == "mean":
                stats.append(x.mean(dim=2))
            elif stat == "max":
                stats.append(x.max(dim=2)[0])
            elif stat == "min":
                stats.append(x.min(dim=2)[0])
            elif stat == "std":
                stats.append(x.std(dim=2))
        
        return torch.cat(stats, dim=1)
    
    def forward(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, channels, seq_length)
            lengths: Optional tensor of original sequence lengths for masking
        
        Returns:
            Output tensor of shape (batch_size, n_classes)
        """
        # Convolutional layers
        x = self.conv_layers(x)  # (batch, cnn_channels[-1], reduced_seq_len)
        
        # Multi-Statistics Pooling (with masking if lengths provided)
        x = self._multiStatsPool(x, lengths)  # (batch, cnn_channels[-1] * n_stats)
        
        # Classifier
        x = self.dropout(x)
        x = self.fc(x)  # (batch, n_classes)
        
        return x
    
    def getModelConfig(self) -> Dict[str, Any]:
        """
        Get model configuration for saving.
        
        Returns:
            Dictionary containing model configuration
        """
        config = super().getModelConfig()
        config.update({
            "cnn_channels": self.cnn_channels,
            "kernel_size": self.kernel_size,
            "dropout": self.dropout_rate,
            "pool_stats": self.pool_stats,
        })
        return config


class CnnClassifierWithAttention(BaseClassifier):
    """
    1D CNN classifier with self-attention mechanism.
    
    Architecture:
        Input (batch, channels, seq_len)
        → [Conv1d → BatchNorm → ReLU → MaxPool] × N layers
        → Self-Attention
        → Global Average Pooling
        → Dropout → Linear → Output (batch, n_classes)
    
    Attention allows the model to focus on important time points.
    """
    
    def __init__(
            self,
            input_channels: int = 1,
            n_classes: int = 2,
            cnn_channels: List[int] = None,
            kernel_size: int = 7,
            dropout: float = 0.3,
            attention_heads: int = 4,
        ):
        """
        Initialize the CNN classifier with attention.
        
        Args:
            input_channels: Number of input channels
            n_classes: Number of output classes
            cnn_channels: List of channel sizes for each conv layer
            kernel_size: Kernel size for conv layers
            dropout: Dropout rate
            attention_heads: Number of attention heads
        """
        super().__init__(input_channels, n_classes)
        
        if cnn_channels is None:
            cnn_channels = [32, 64, 128]
        
        self.cnn_channels = cnn_channels
        self.kernel_size = kernel_size
        self.dropout_rate = dropout
        self.attention_heads = attention_heads
        
        # Build convolutional layers
        self.conv_layers = self._buildConvLayers()
        
        # Self-attention layer
        self.attention = nn.MultiheadAttention(
            embed_dim=cnn_channels[-1],
            num_heads=attention_heads,
            dropout=dropout,
            batch_first=True,
        )
        
        # Global Average Pooling
        self.global_avg_pool = nn.AdaptiveAvgPool1d(1)
        
        # Classifier head
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(cnn_channels[-1], n_classes)
    
    def _buildConvLayers(self) -> nn.Sequential:
        """Build the convolutional layers."""
        layers = []
        in_channels = self.input_channels
        
        for out_channels in self.cnn_channels:
            layers.extend([
                nn.Conv1d(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    kernel_size=self.kernel_size,
                    padding=self.kernel_size // 2,
                ),
                nn.BatchNorm1d(out_channels),
                nn.ReLU(inplace=True),
                nn.MaxPool1d(kernel_size=2, stride=2),
            ])
            in_channels = out_channels
        
        return nn.Sequential(*layers)
    
    def forward(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, channels, seq_length)
            lengths: Optional tensor of original sequence lengths
        
        Returns:
            Output tensor of shape (batch_size, n_classes)
        """
        # Convolutional layers
        x = self.conv_layers(x)  # (batch, cnn_channels[-1], reduced_seq_len)
        
        # Transpose for attention: (batch, seq_len, channels)
        x = x.transpose(1, 2)
        
        # Self-attention
        x, _ = self.attention(x, x, x)  # (batch, seq_len, channels)
        
        # Transpose back: (batch, channels, seq_len)
        x = x.transpose(1, 2)
        
        # Global Average Pooling
        x = self.global_avg_pool(x)  # (batch, channels, 1)
        x = x.squeeze(-1)  # (batch, channels)
        
        # Classifier
        x = self.dropout(x)
        x = self.fc(x)  # (batch, n_classes)
        
        return x
    
    def getModelConfig(self) -> Dict[str, Any]:
        """Get model configuration for saving."""
        config = super().getModelConfig()
        config.update({
            "cnn_channels": self.cnn_channels,
            "kernel_size": self.kernel_size,
            "dropout": self.dropout_rate,
            "attention_heads": self.attention_heads,
        })
        return config