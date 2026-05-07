"""Backend factory and utilities."""

from kcp.backends.base import Backend
from kcp.backends.mem_backend import MemBackend
from kcp.backends.api_backend import ApiBackend
from kcp.config import CompressorConfig, MemConfig, ApiConfig


def create_backend(config: CompressorConfig) -> Backend:
    """Create backend instance from config.

    Args:
        config: Compressor configuration.

    Returns:
        Initialized backend.
    """
    if isinstance(config, MemConfig):
        return MemBackend(config)
    elif isinstance(config, ApiConfig):
        return ApiBackend(config)
    else:
        raise ValueError(f"Unknown config type: {type(config)}")


__all__ = ["Backend", "MemBackend", "ApiBackend", "create_backend"]
