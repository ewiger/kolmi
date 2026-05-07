"""Example usage of KCP compression for NID calculations."""

import numpy as np
from kcp.config import MemConfig
from kcp.library import compress_text


def approximate_nid(text_a: str, text_b: str, config: MemConfig) -> float:
    """Approximate Normalized Information Distance using compression.

    NID ≈ (K(xy) - min(K(x), K(y))) / max(K(x), K(y))

    Where K(x) ≈ len(compress(x))

    Args:
        text_a: First text sample.
        text_b: Second text sample.
        config: Compression config (must be deterministic).

    Returns:
        Approximated NID value in range [0, 1].
    """
    try:
        # Compute compressed sizes
        K_x = len(compress_text(text_a, config))
        K_y = len(compress_text(text_b, config))
        K_xy = len(compress_text(text_a + text_b, config))

        # Compute NID
        nid = (K_xy - min(K_x, K_y)) / max(K_x, K_y)
        return max(0.0, min(1.0, nid))  # Clamp to [0, 1]

    except Exception as e:
        print(f"Error computing NID: {e}")
        return -1.0


if __name__ == "__main__":
    # Example: Compare similarity of two texts
    text1 = "The quick brown fox jumps over the lazy dog"
    text2 = "The quick brown fox jumps over the lazy cat"
    text3 = "Machine learning is fascinating"

    # Create a deterministic config (requires a model)
    config = MemConfig(
        model_path="distilgpt2",
        context_size=256,
        cdf_precision=16,
        verbose=True,
    )

    print("Computing NID values...\n")

    try:
        nid_12 = approximate_nid(text1, text2, config)
        print(f"NID(text1, text2) = {nid_12:.4f}  (similar texts)")

        nid_13 = approximate_nid(text1, text3, config)
        print(f"NID(text1, text3) = {nid_13:.4f}  (different texts)")

    except Exception as e:
        print(f"Example failed (likely missing model): {e}\n")
        print("To run this example, install a model first:")
        print("  python -c \"from transformers import AutoModel; AutoModel.from_pretrained('distilgpt2')\"")
