"""Archive format I/O (headers, metadata, checksums)."""

import io
import json
import struct
from typing import Dict, Any, Tuple
import hashlib


MAGIC = b"KCP\x01"
VERSION = 1


def write_archive(
    raw_bitstream: bytes,
    config_dict: Dict[str, Any],
    mode: str,
) -> bytes:
    """Wrap raw bitstream in archive format with metadata.

    Args:
        raw_bitstream: Raw compressed data (no header).
        config_dict: Configuration dict (for metadata).
        mode: "mem" or "api".

    Returns:
        Complete archive as bytes.
    """
    archive = io.BytesIO()

    # Magic and version
    archive.write(MAGIC)
    archive.write(bytes([VERSION]))

    # Mode
    mode_byte = 0x00 if mode == "mem" else 0x01
    archive.write(bytes([mode_byte]))

    # Metadata as JSON
    metadata = {
        "mode": mode,
        "config": config_dict,
        "cdf_precision": config_dict.get("cdf_precision", 16),
        "context_size": config_dict.get("context_size", 256),
        "eos_token_id": config_dict.get("eos_token_id", 2),
    }
    metadata_json = json.dumps(metadata)
    metadata_bytes = metadata_json.encode("utf-8")

    # Write metadata size (4 bytes, little-endian)
    archive.write(struct.pack("<I", len(metadata_bytes)))
    archive.write(metadata_bytes)

    # Checksum of raw bitstream (blake2b, 32 bytes)
    checksum = hashlib.blake2b(raw_bitstream, digest_size=32).digest()
    archive.write(checksum)

    # Raw bitstream payload
    archive.write(raw_bitstream)

    return archive.getvalue()


def read_archive(archive_bytes: bytes) -> Tuple[bytes, Dict[str, Any], str]:
    """Extract metadata and raw bitstream from archive.

    Args:
        archive_bytes: Archive data.

    Returns:
        (raw_bitstream, metadata_dict, mode)

    Raises:
        ValueError: If archive format is invalid.
    """
    reader = io.BytesIO(archive_bytes)

    # Check magic
    magic = reader.read(4)
    if magic != MAGIC:
        raise ValueError(f"Invalid archive magic: {magic!r}, expected {MAGIC!r}")

    # Check version
    version = reader.read(1)
    if not version or version[0] != VERSION:
        raise ValueError(f"Unsupported archive version: {version!r}")

    # Read mode
    mode_byte = reader.read(1)
    if not mode_byte:
        raise ValueError("Archive truncated: missing mode")
    mode = "mem" if mode_byte[0] == 0x00 else "api"

    # Read metadata
    metadata_size_bytes = reader.read(4)
    if len(metadata_size_bytes) < 4:
        raise ValueError("Archive truncated: missing metadata size")
    metadata_size = struct.unpack("<I", metadata_size_bytes)[0]

    metadata_bytes = reader.read(metadata_size)
    if len(metadata_bytes) < metadata_size:
        raise ValueError("Archive truncated: incomplete metadata")

    try:
        metadata = json.loads(metadata_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid metadata JSON: {e}") from e

    # Read checksum (32 bytes)
    checksum = reader.read(32)
    if len(checksum) < 32:
        raise ValueError("Archive truncated: missing checksum")

    # Read payload
    raw_bitstream = reader.read()

    # Verify checksum
    expected_checksum = hashlib.blake2b(raw_bitstream, digest_size=32).digest()
    if checksum != expected_checksum:
        raise ValueError(
            f"Checksum mismatch: archive may be corrupted or payload altered"
        )

    return raw_bitstream, metadata, mode
