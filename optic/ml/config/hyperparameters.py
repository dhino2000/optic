"""
Hyperparameters configuration for ROI classifier training.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json


@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing."""
    fneu_coefficient: float = 0.7           # F - Fneu * coef
    baseline_percentile: float = 10.0       # Percentile for baseline calculation in dF/F0
    # For future extension (e.g., class imbalance handling)
    normalize_method: Optional[str] = None  # None, "zscore", "minmax"
    
    def toDict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def fromDict(cls, config_dict: Dict[str, Any]) -> "PreprocessingConfig":
        return cls(**config_dict)


@dataclass
class ModelConfig:
    """Configuration for model architecture."""
    model_type: str = "cnn"                 # "cnn" or "rnn"
    input_channels: int = 1                 # Number of input channels
    n_classes: int = 2                      # Number of classification classes
    # CNN-specific settings
    cnn_channels: List[int] = field(default_factory=lambda: [32, 64, 128])
    cnn_kernel_size: int = 7
    cnn_dropout: float = 0.3
    # RNN-specific settings
    rnn_hidden_size: int = 128
    rnn_num_layers: int = 2
    rnn_dropout: float = 0.3
    rnn_bidirectional: bool = True
    
    def toDict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def fromDict(cls, config_dict: Dict[str, Any]) -> "ModelConfig":
        return cls(**config_dict)


@dataclass
class TrainingConfig:
    """Configuration for training."""
    # Basic settings
    n_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    # K-fold settings
    k_fold: int = 5
    # Checkpoint settings
    checkpoint_interval: int = 10           # Save checkpoint every N epochs
    # Early stopping (for future extension)
    early_stopping: bool = False
    early_stopping_patience: int = 10
    # Class imbalance handling (for future extension)
    use_class_weights: bool = False
    
    def toDict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def fromDict(cls, config_dict: Dict[str, Any]) -> "TrainingConfig":
        return cls(**config_dict)


@dataclass
class ClassifierConfig:
    """Configuration class that combines all settings for ROI classifier."""
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    # Classification class names
    class_names: List[str] = field(default_factory=lambda: ["Neuron", "Not_Cell"])
    
    def __post_init__(self):
        # Sync n_classes with the length of class_names
        self.model.n_classes = len(self.class_names)
    
    def toDict(self) -> Dict[str, Any]:
        return {
            "preprocessing": self.preprocessing.toDict(),
            "model": self.model.toDict(),
            "training": self.training.toDict(),
            "class_names": self.class_names,
        }
    
    @classmethod
    def fromDict(cls, config_dict: Dict[str, Any]) -> "ClassifierConfig":
        return cls(
            preprocessing=PreprocessingConfig.fromDict(config_dict.get("preprocessing", {})),
            model=ModelConfig.fromDict(config_dict.get("model", {})),
            training=TrainingConfig.fromDict(config_dict.get("training", {})),
            class_names=config_dict.get("class_names", ["Neuron", "Not_Cell"]),
        )
    
    def toJson(self, path: str) -> None:
        """Save configuration to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.toDict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def fromJson(cls, path: str) -> "ClassifierConfig":
        """Load configuration from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        return cls.fromDict(config_dict)
    
    def validate(self) -> List[str]:
        """Validate configuration and return a list of error messages."""
        errors = []
        
        # Validate preprocessing config
        if not 0 <= self.preprocessing.fneu_coefficient <= 1:
            errors.append("fneu_coefficient must be between 0 and 1")
        if not 0 < self.preprocessing.baseline_percentile < 100:
            errors.append("baseline_percentile must be between 0 and 100")
        
        # Validate model config
        if self.model.model_type not in ["cnn", "rnn"]:
            errors.append("model_type must be 'cnn' or 'rnn'")
        if self.model.n_classes < 2:
            errors.append("n_classes must be at least 2")
        if len(self.class_names) != self.model.n_classes:
            errors.append("class_names length must match n_classes")
        
        # Validate training config
        if self.training.n_epochs < 1:
            errors.append("n_epochs must be at least 1")
        if self.training.batch_size < 1:
            errors.append("batch_size must be at least 1")
        if self.training.k_fold < 2:
            errors.append("k_fold must be at least 2")
        if self.training.learning_rate <= 0:
            errors.append("learning_rate must be positive")
        
        return errors


# Function to get default configuration
def getDefaultConfig() -> ClassifierConfig:
    """Return default classifier configuration."""
    return ClassifierConfig()


def getDefaultHyperparametersForGUI() -> Dict[str, Dict[str, Any]]:
    """
    Return hyperparameter information for GUI display.
    Includes display name, type, range, etc. for each parameter.
    """
    return {
        "preprocessing": {
            "fneu_coefficient": {
                "display_name": "Fneu Coefficient",
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "default": 0.7,
            },
            "baseline_percentile": {
                "display_name": "Baseline Percentile",
                "type": "float",
                "min": 1.0,
                "max": 50.0,
                "step": 1.0,
                "default": 10.0,
            },
        },
        "training": {
            "n_epochs": {
                "display_name": "Number of Epochs",
                "type": "int",
                "min": 1,
                "max": 1000,
                "step": 10,
                "default": 100,
            },
            "batch_size": {
                "display_name": "Batch Size",
                "type": "int",
                "min": 1,
                "max": 256,
                "step": 8,
                "default": 32,
            },
            "learning_rate": {
                "display_name": "Learning Rate",
                "type": "float",
                "min": 1e-6,
                "max": 1e-1,
                "step": 1e-4,
                "default": 1e-3,
            },
            "weight_decay": {
                "display_name": "Weight Decay",
                "type": "float",
                "min": 0.0,
                "max": 1e-2,
                "step": 1e-5,
                "default": 1e-4,
            },
            "k_fold": {
                "display_name": "K-Fold",
                "type": "int",
                "min": 2,
                "max": 10,
                "step": 1,
                "default": 5,
            },
            "checkpoint_interval": {
                "display_name": "Checkpoint Interval (epochs)",
                "type": "int",
                "min": 1,
                "max": 100,
                "step": 5,
                "default": 10,
            },
        },
    }