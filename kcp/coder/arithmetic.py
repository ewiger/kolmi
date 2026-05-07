"""Arithmetic coder for range-based compression."""

import io
import struct
from typing import Tuple


class ArithmeticEncoder:
    """Deterministic arithmetic range encoder."""

    def __init__(self, cdf_precision: int = 16):
        """Initialize encoder.

        Args:
            cdf_precision: Precision bits for CDF values.
        """
        self.cdf_precision = cdf_precision
        self.bits = []

    def encode(self, cdf: list, symbol: int, cdf_max: int) -> None:
        """Encode a symbol using its CDF.

        Args:
            cdf: Cumulative distribution array.
            symbol: Symbol index.
            cdf_max: Maximum CDF value.
        """
        # Get the CDF interval for this symbol
        low_val = cdf[symbol]
        high_val = cdf[symbol + 1] if symbol + 1 < len(cdf) else cdf_max
        
        # Encode the low value using cdf_precision bits
        for i in range(self.cdf_precision):
            bit = (low_val >> (self.cdf_precision - 1 - i)) & 1
            self.bits.append(bit)

    def finish(self) -> bytes:
        """Finalize encoding and return compressed bitstream."""
        # Pad to byte boundary
        while len(self.bits) % 8 != 0:
            self.bits.append(0)
        
        # Convert bits to bytes
        output = io.BytesIO()
        for i in range(0, len(self.bits), 8):
            byte_val = 0
            for j in range(8):
                byte_val = (byte_val << 1) | self.bits[i + j]
            output.write(bytes([byte_val]))
        
        return output.getvalue()


class ArithmeticDecoder:
    """Deterministic arithmetic range decoder."""

    def __init__(self, bitstream: bytes, cdf_precision: int = 16):
        """Initialize decoder.

        Args:
            bitstream: Compressed bitstream.
            cdf_precision: Precision bits for CDF values.
        """
        self.cdf_precision = cdf_precision
        self.bits = []
        
        # Convert bytes to bits
        for byte in bitstream:
            for i in range(8):
                self.bits.append((byte >> (7 - i)) & 1)
        
        self.bit_pos = 0

    def decode(self, cdf: list, cdf_max: int) -> int:
        """Decode next symbol using CDF.

        Args:
            cdf: Cumulative distribution array.
            cdf_max: Maximum CDF value.

        Returns:
            Decoded symbol index.
        """
        # Read cdf_precision bits
        value = 0
        for i in range(self.cdf_precision):
            if self.bit_pos < len(self.bits):
                value = (value << 1) | self.bits[self.bit_pos]
                self.bit_pos += 1
            else:
                break
        
        # Find which symbol this value corresponds to
        # The value represents a position in the CDF
        symbol = 0
        for i in range(len(cdf) - 1):
            if value >= cdf[i] and value < cdf[i + 1]:
                symbol = i
                break
        else:
            # If not found, it's the last symbol
            symbol = len(cdf) - 2
        
        return symbol
