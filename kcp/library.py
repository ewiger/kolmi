"""Library API for text compression with and without archiving."""

from typing import Optional
from kcp.config import CompressorConfig, MemConfig
from kcp.core import KCPCompressor
from kcp.format import write_archive, read_archive


# ============================================================================
# CORE LAYER: Raw compression (no headers, for NID/K-complexity use)
# ============================================================================


def compress_text(text: str, config: CompressorConfig) -> bytes:
    """Compress text to raw bitstream without headers.

    This is the low-level API for K-complexity approximation and NID calculations.
    The output contains only the compressed data—no metadata, magic bytes, or versioning.

    Args:
        text: Text to compress.
        config: CompressorConfig instance.

    Returns:
        Raw compressed bitstream (bytes).

    Example:
        >>> from kcp import compress_text
        >>> from kcp.config import MemConfig
        >>> config = MemConfig(model_path="path/to/model")
        >>> bitstream = compress_text("hello world", config)
        >>> len(bitstream)  # Compressed size in bytes
    """
    compressor = KCPCompressor(config)
    return compressor.compress(text)


def decompress_text(bitstream: bytes, config: CompressorConfig) -> str:
    """Decompress raw bitstream without headers.

    This is the low-level API for K-complexity approximation and NID calculations.
    Config must match exactly the config used during compression.

    Args:
        bitstream: Raw compressed bitstream.
        config: CompressorConfig instance (must match encoder's config).

    Returns:
        Decompressed text.

    Raises:
        RuntimeError: If config mismatch or decompression fails.

    Example:
        >>> text = decompress_text(bitstream, config)
    """
    compressor = KCPCompressor(config)
    return compressor.decompress(bitstream)


# ============================================================================
# ARCHIVE LAYER: Compression with metadata (for portable file storage)
# ============================================================================


def archive_compress(text: str, config: CompressorConfig, output_path: Optional[str] = None) -> bytes:
    """Compress text and wrap in archive format with headers and metadata.

    This is the high-level API for portable, reproducible file storage.
    The output includes magic bytes, versioning, metadata, integrity checksum, and payload.

    Args:
        text: Text to compress.
        config: CompressorConfig instance.
        output_path: Optional file path to write archive to. If None, returns bytes in memory.

    Returns:
        Archive bytes if output_path is None, else returns archive bytes (also writes to file).

    Example:
        >>> from kcp import archive_compress
        >>> from kcp.config import MemConfig
        >>> config = MemConfig(model_path="path/to/model")
        >>> archive_bytes = archive_compress("hello world", config)
        >>> # or write to file:
        >>> archive_bytes = archive_compress("hello world", config, output_path="out.kcp")
    """
    # Compress using core layer
    bitstream = compress_text(text, config)

    # Prepare config dict for metadata
    config_dict = {
        "mode": config.mode,
        "context_size": config.context_size,
        "cdf_precision": config.cdf_precision,
        "eos_token_id": config.eos_token_id,
    }

    # Add mode-specific metadata
    if hasattr(config, "get_config_hash"):
        config_dict["config_hash"] = config.get_config_hash()
    if hasattr(config, "model_path"):
        config_dict["model_path"] = config.model_path
    if hasattr(config, "provider"):
        config_dict["provider"] = config.provider
        config_dict["api_model"] = config.api_model

    # Create archive
    archive_bytes = write_archive(bitstream, config_dict, config.mode)

    # Write to file if requested
    if output_path:
        with open(output_path, "wb") as f:
            f.write(archive_bytes)

    return archive_bytes


def archive_decompress(
    archive_data,  # bytes or file path str
    config_override: Optional[dict] = None,
) -> str:
    """Decompress archive format and extract text.

    This is the high-level API for reading portable archive files.
    Metadata is extracted from the archive; config_override can be used to force settings.

    Args:
        archive_data: Archive bytes or file path (str).
        config_override: Optional dict to override extracted config.

    Returns:
        Decompressed text.

    Raises:
        ValueError: If archive format is invalid.
        RuntimeError: If decompression fails.

    Example:
        >>> from kcp import archive_decompress
        >>> text = archive_decompress("out.kcp")
        >>> # or from bytes:
        >>> text = archive_decompress(archive_bytes)
    """
    # Load archive data
    if isinstance(archive_data, str):
        with open(archive_data, "rb") as f:
            archive_bytes = f.read()
    else:
        archive_bytes = archive_data

    # Parse archive
    bitstream, metadata, mode = read_archive(archive_bytes)

    # Reconstruct config
    config_data = metadata.get("config", {})

    if config_override:
        config_data.update(config_override)

    # Build config object
    if mode == "mem":
        config = MemConfig(
            model_path=config_data.get("model_path"),
            context_size=config_data.get("context_size", 256),
            cdf_precision=config_data.get("cdf_precision", 16),
            eos_token_id=config_data.get("eos_token_id", 2),
        )
    else:
        from kcp.config import ApiConfig

        config = ApiConfig(
            provider=config_data.get("provider", "ollama"),
            api_model=config_data.get("api_model", "llama2"),
            context_size=config_data.get("context_size", 256),
            cdf_precision=config_data.get("cdf_precision", 16),
            eos_token_id=config_data.get("eos_token_id", 2),
        )

    # Decompress
    return decompress_text(bitstream, config)


__all__ = [
    "compress_text",
    "decompress_text",
    "archive_compress",
    "archive_decompress",
]
