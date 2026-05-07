"""Configuration types for KCP compression modes."""

from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class CompressorConfig:
    """Base compressor configuration."""

    mode: Literal["mem", "api"]
    context_size: int = 256
    cdf_precision: int = 16
    eos_token_id: int = 2  # Common EOS token ID
    verbose: bool = False


@dataclass
class MemConfig(CompressorConfig):
    """In-memory model backend configuration."""

    mode: Literal["mem"] = "mem"
    model_path: Optional[str] = None
    tokenizer_path: Optional[str] = None
    device: str = "cpu"
    dtype: str = "float32"
    models_dir: Optional[str] = None  # Local models directory; None = use KCP_MODELS_DIR or default

    def get_config_hash(self) -> str:
        """Return deterministic hash of config for reproducibility checks."""
        import hashlib
        import json

        config_dict = {
            "mode": self.mode,
            "model_path": self.model_path,
            "tokenizer_path": self.tokenizer_path,
            "device": self.device,
            "dtype": self.dtype,
            "context_size": self.context_size,
            "cdf_precision": self.cdf_precision,
            "eos_token_id": self.eos_token_id,
        }
        config_json = json.dumps(config_dict, sort_keys=True)
        return hashlib.blake2b(config_json.encode(), digest_size=32).hexdigest()


@dataclass
class ApiConfig(CompressorConfig):
    """API backend configuration."""

    mode: Literal["api"] = "api"
    provider: str = "ollama"  # ollama, openai, custom
    api_base: str = "http://localhost:11434"
    api_key: Optional[str] = None
    api_model: str = "llama2"
    timeout: float = 30.0
    max_retries: int = 3

    def get_config_hash(self) -> str:
        """Return deterministic hash of config for reproducibility checks."""
        import hashlib
        import json

        config_dict = {
            "mode": self.mode,
            "provider": self.provider,
            "api_base": self.api_base,
            "api_model": self.api_model,
            "context_size": self.context_size,
            "cdf_precision": self.cdf_precision,
            "eos_token_id": self.eos_token_id,
        }
        config_json = json.dumps(config_dict, sort_keys=True)
        return hashlib.blake2b(config_json.encode(), digest_size=32).hexdigest()
