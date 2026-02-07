"""
RNN/LSTM classifier model for ROI classification.
Uses final hidden state for classification, naturally handles variable-length sequences.
"""
from __future__ import annotations
import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from typing import Dict, Any, Optional

from .base_model import BaseClassifier


class RnnClassifier(BaseClassifier):
    """
    LSTM-based classifier for ROI classification.
    
    Architecture:
        Input (batch, channels, seq_len)
        → Linear projection (optional)
        → LSTM
        → Final hidden state
        → Dropout → Linear → Output (batch, n_classes)
    
    LSTM naturally handles variable-length sequences.
    Uses pack_padded_sequence for efficient computation with padded batches.
    """
    
    def __init__(
            self,
            input_channels: int = 1,
            n_classes: int = 2,
            hidden_size: int = 128,
            num_layers: int = 2,
            dropout: float = 0.3,
            bidirectional: bool = True,
        ):
        """
        Initialize the RNN classifier.
        
        Args:
            input_channels: Number of input channels
            n_classes: Number of output classes
            hidden_size: LSTM hidden state size
            num_layers: Number of LSTM layers
            dropout: Dropout rate
            bidirectional: Whether to use bidirectional LSTM
        """
        super().__init__(input_channels, n_classes)
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_rate = dropout
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_channels,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
        )
        
        # Classifier head
        classifier_input_size = hidden_size * self.num_directions
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(classifier_input_size, n_classes)
    
    def forward(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, channels, seq_length)
            lengths: Tensor of original sequence lengths (batch_size,)
                     Required for proper handling of padded sequences
        
        Returns:
            Output tensor of shape (batch_size, n_classes)
        """
        batch_size = x.size(0)
        
        # Transpose: (batch, channels, seq_len) -> (batch, seq_len, channels)
        x = x.transpose(1, 2)
        
        # Pack padded sequence if lengths are provided
        if lengths is not None:
            # Ensure lengths are on CPU and sorted for pack_padded_sequence
            lengths_cpu = lengths.cpu()
            
            # Pack sequence
            x_packed = pack_padded_sequence(
                x, lengths_cpu, batch_first=True, enforce_sorted=False
            )
            
            # LSTM forward
            _, (h_n, _) = self.lstm(x_packed)
        else:
            # LSTM forward without packing
            _, (h_n, _) = self.lstm(x)
        
        # h_n shape: (num_layers * num_directions, batch, hidden_size)
        # Get the last layer's hidden state
        if self.bidirectional:
            # Concatenate forward and backward hidden states
            h_forward = h_n[-2, :, :]  # (batch, hidden_size)
            h_backward = h_n[-1, :, :]  # (batch, hidden_size)
            h_final = torch.cat([h_forward, h_backward], dim=1)  # (batch, hidden_size * 2)
        else:
            h_final = h_n[-1, :, :]  # (batch, hidden_size)
        
        # Classifier
        x = self.dropout(h_final)
        x = self.fc(x)  # (batch, n_classes)
        
        return x
    
    def getModelConfig(self) -> Dict[str, Any]:
        """Get model configuration for saving."""
        config = super().getModelConfig()
        config.update({
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "dropout": self.dropout_rate,
            "bidirectional": self.bidirectional,
        })
        return config


class GruClassifier(BaseClassifier):
    """
    GRU-based classifier for ROI classification.
    
    Similar to RnnClassifier but uses GRU instead of LSTM.
    GRU is simpler and often faster while achieving similar performance.
    """
    
    def __init__(
            self,
            input_channels: int = 1,
            n_classes: int = 2,
            hidden_size: int = 128,
            num_layers: int = 2,
            dropout: float = 0.3,
            bidirectional: bool = True,
        ):
        """
        Initialize the GRU classifier.
        
        Args:
            input_channels: Number of input channels
            n_classes: Number of output classes
            hidden_size: GRU hidden state size
            num_layers: Number of GRU layers
            dropout: Dropout rate
            bidirectional: Whether to use bidirectional GRU
        """
        super().__init__(input_channels, n_classes)
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_rate = dropout
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        # GRU layer
        self.gru = nn.GRU(
            input_size=input_channels,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional,
        )
        
        # Classifier head
        classifier_input_size = hidden_size * self.num_directions
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(classifier_input_size, n_classes)
    
    def forward(
            self, 
            x: torch.Tensor, 
            lengths: Optional[torch.Tensor] = None
        ) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape (batch_size, channels, seq_length)
            lengths: Tensor of original sequence lengths (batch_size,)
        
        Returns:
            Output tensor of shape (batch_size, n_classes)
        """
        batch_size = x.size(0)
        
        # Transpose: (batch, channels, seq_len) -> (batch, seq_len, channels)
        x = x.transpose(1, 2)
        
        # Pack padded sequence if lengths are provided
        if lengths is not None:
            lengths_cpu = lengths.cpu()
            x_packed = pack_padded_sequence(
                x, lengths_cpu, batch_first=True, enforce_sorted=False
            )
            _, h_n = self.gru(x_packed)
        else:
            _, h_n = self.gru(x)
        
        # h_n shape: (num_layers * num_directions, batch, hidden_size)
        if self.bidirectional:
            h_forward = h_n[-2, :, :]
            h_backward = h_n[-1, :, :]
            h_final = torch.cat([h_forward, h_backward], dim=1)
        else:
            h_final = h_n[-1, :, :]
        
        # Classifier
        x = self.dropout(h_final)
        x = self.fc(x)
        
        return x
    
    def getModelConfig(self) -> Dict[str, Any]:
        """Get model configuration for saving."""
        config = super().getModelConfig()
        config.update({
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "dropout": self.dropout_rate,
            "bidirectional": self.bidirectional,
        })
        return config