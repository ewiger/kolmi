"""Test suite for KCP compression."""

import pytest
import numpy as np
from kcp.probability import logits_to_cdf, probs_to_cdf
from kcp.coder import ArithmeticEncoder, ArithmeticDecoder
from kcp.format import write_archive, read_archive


class TestProbability:
    """Tests for logits-to-CDF conversion."""

    def test_logits_to_cdf_monotonic(self):
        """CDF should be monotonically increasing."""
        logits = np.random.randn(100)
        cdf, cdf_max = logits_to_cdf(logits, cdf_precision=16)

        # Check monotonicity
        for i in range(len(cdf) - 1):
            assert cdf[i] <= cdf[i + 1], f"CDF not monotonic at {i}"

        # Check bounds
        assert cdf[0] == 0
        assert cdf[-1] == cdf_max

    def test_probs_to_cdf_sum(self):
        """CDF should cover full range."""
        probs = np.array([0.2, 0.3, 0.5])
        cdf, cdf_max = probs_to_cdf(probs, cdf_precision=16)

        # Check structure
        assert len(cdf) == len(probs) + 1
        assert cdf[0] == 0
        assert cdf[-1] == cdf_max

    def test_determinism(self):
        """Same logits should produce same CDF."""
        logits = np.array([1.0, 2.0, 3.0, 0.5])

        cdf1, max1 = logits_to_cdf(logits, cdf_precision=16)
        cdf2, max2 = logits_to_cdf(logits, cdf_precision=16)

        np.testing.assert_array_equal(cdf1, cdf2)
        assert max1 == max2


class TestArithmeticCoder:
    """Tests for arithmetic encoder/decoder."""

    def test_encode_decode_single_symbol(self):
        """Encode and decode single symbol."""
        # Create simple CDF: uniform over 4 symbols
        cdf = [0, 4096, 8192, 12288, 16384]
        cdf_max = 16384
        symbol = 2

        encoder = ArithmeticEncoder(cdf_precision=14)
        encoder.encode(cdf, symbol, cdf_max)
        bitstream = encoder.finish()

        # Decode
        decoder = ArithmeticDecoder(bitstream, cdf_precision=14)
        decoded = decoder.decode(cdf, cdf_max)

        assert decoded == symbol

    def test_encode_decode_multiple_symbols(self):
        """Encode and decode multiple symbols."""
        cdf = [0, 4096, 8192, 12288, 16384]
        cdf_max = 16384
        symbols = [0, 1, 2, 3, 2, 1, 0]

        encoder = ArithmeticEncoder(cdf_precision=14)
        for sym in symbols:
            encoder.encode(cdf, sym, cdf_max)
        bitstream = encoder.finish()

        # Decode
        decoder = ArithmeticDecoder(bitstream, cdf_precision=14)
        decoded = []
        for _ in range(len(symbols)):
            decoded.append(decoder.decode(cdf, cdf_max))

        assert decoded == symbols


class TestArchiveFormat:
    """Tests for archive format I/O."""

    def test_write_read_archive(self):
        """Write and read archive roundtrip."""
        bitstream = b"\x00\x01\x02\x03" * 10
        config = {"model": "test", "cdf_precision": 16}
        mode = "mem"

        archive = write_archive(bitstream, config, mode)
        restored_bitstream, metadata, restored_mode = read_archive(archive)

        assert restored_bitstream == bitstream
        assert restored_mode == mode
        assert metadata["config"]["model"] == "test"

    def test_archive_checksum_verification(self):
        """Archive checksum should detect tampering."""
        bitstream = b"original data"
        config = {"model": "test"}
        mode = "mem"

        archive = bytearray(write_archive(bitstream, config, mode))

        # Tamper with payload (skip magic + version + mode + metadata)
        # Find payload start (after checksum)
        archive[-5] ^= 0xFF  # Flip a bit in the payload

        # Corrupted archive should fail
        with pytest.raises(ValueError, match="Checksum mismatch"):
            read_archive(bytes(archive))


class TestIntegration:
    """Integration tests for full compression pipeline."""

    def test_round_trip_identity(self):
        """Basic round-trip test (without actual model)."""
        # This test would require a real model or mock backend
        # Placeholder for full integration test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
