"""KCP: Kolmi Compressor using LLM probabilities and arithmetic coding."""

__version__ = "0.1.0"

from kcp.library import compress_text, decompress_text, archive_compress, archive_decompress

__all__ = [
    "compress_text",
    "decompress_text",
    "archive_compress",
    "archive_decompress",
]
