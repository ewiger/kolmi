"""Core compression and decompression orchestration."""

from typing import Optional
import numpy as np
from kcp.config import CompressorConfig
from kcp.backends import create_backend
from kcp.coder import ArithmeticEncoder, ArithmeticDecoder
from kcp.probability import logits_to_cdf


class KCPCompressor:
    """Core compressor using backend logits and arithmetic coding."""

    def __init__(self, config: CompressorConfig):
        """Initialize compressor.

        Args:
            config: Compressor configuration.
        """
        self.config = config
        self.backend = create_backend(config)
        self.backend.initialize()

    def compress(self, text: str) -> bytes:
        """Compress text to raw bitstream (no headers).

        Args:
            text: Input text to compress.

        Returns:
            Raw compressed bitstream (bytes).

        Notes:
            - Output contains no headers or metadata.
            - Decompression requires identical config.
        """
        # Tokenize input
        try:
            tokens = self.backend.tokenizer.encode(text)
        except AttributeError:
            raise RuntimeError(
                "Backend does not support tokenization. "
                "Use MemBackend for text compression."
            )

        if self.config.verbose:
            print(f"Tokenized text: {len(tokens)} tokens")

        # Initialize encoder
        encoder = ArithmeticEncoder(cdf_precision=self.config.cdf_precision)

        # Encode each token
        context = [self.config.eos_token_id]  # Start with EOS as initial state
        for i, token in enumerate(tokens):
            if self.config.verbose and (i + 1) % 100 == 0:
                print(f"  Encoded {i + 1}/{len(tokens)} tokens")

            # Get logits from backend
            logits = self.backend.get_next_token_logits(context)

            # Convert to CDF
            cdf, cdf_max = logits_to_cdf(logits, cdf_precision=self.config.cdf_precision)

            # Encode token
            encoder.encode(cdf.tolist(), token, cdf_max)

            # Update context
            context.append(token)
            context = context[-(self.config.context_size) :]

        # Encode EOS token as end marker
        logits = self.backend.get_next_token_logits(context)
        cdf, cdf_max = logits_to_cdf(logits, cdf_precision=self.config.cdf_precision)
        encoder.encode(cdf.tolist(), self.config.eos_token_id, cdf_max)

        bitstream = encoder.finish()

        if self.config.verbose:
            print(f"Compressed size: {len(bitstream)} bytes")

        return bitstream

    def decompress(self, bitstream: bytes) -> str:
        """Decompress raw bitstream (no headers).

        Args:
            bitstream: Raw compressed bitstream.

        Returns:
            Decompressed text.

        Raises:
            RuntimeError: If backend or config mismatch.
        """
        # Initialize decoder
        decoder = ArithmeticDecoder(bitstream, cdf_precision=self.config.cdf_precision)

        # Decode tokens
        tokens = []
        context = [self.config.eos_token_id]  # Start with EOS
        max_tokens = 1000000  # Safety limit

        while len(tokens) < max_tokens:
            # Get logits from backend
            logits = self.backend.get_next_token_logits(context)

            # Convert to CDF
            cdf, cdf_max = logits_to_cdf(logits, cdf_precision=self.config.cdf_precision)

            # Decode token
            try:
                token = decoder.decode(cdf.tolist(), cdf_max)
            except Exception as e:
                if self.config.verbose:
                    print(f"Decode error at token {len(tokens)}: {e}")
                break

            # Check for EOS
            if token == self.config.eos_token_id:
                break

            tokens.append(token)
            context.append(token)
            context = context[-(self.config.context_size) :]

            if self.config.verbose and (len(tokens) + 1) % 100 == 0:
                print(f"  Decoded {len(tokens)} tokens")

        # Detokenize
        try:
            text = self.backend.tokenizer.decode(tokens)
        except AttributeError:
            raise RuntimeError(
                "Backend does not support detokenization. "
                "Use MemBackend for text decompression."
            )

        if self.config.verbose:
            print(f"Decompressed {len(tokens)} tokens to {len(text)} characters")

        return text
