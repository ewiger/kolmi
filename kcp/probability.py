"""Conversion from logits/probabilities to deterministic integer CDFs."""

import numpy as np
from typing import Tuple


def logits_to_cdf(
    logits: np.ndarray, cdf_precision: int = 16, min_prob: float = 1e-8
) -> Tuple[np.ndarray, int]:
    """Convert logits to cumulative distribution function with integer precision.

    Args:
        logits: Raw model logits, shape (vocab_size,).
        cdf_precision: Bits of precision for integer CDF (typically 16-24).
        min_prob: Minimum probability floor to avoid zero probabilities.

    Returns:
        cdf: Cumulative distribution array, shape (vocab_size+1,) with dtype uint32/uint64.
        cdf_max: Maximum CDF value (2^cdf_precision - 1).

    Determinism guarantee:
        - Uses stable log-sum-exp via numpy (float64 for intermediate precision).
        - Applies floor probability to ensure all tokens are decodable.
        - CDF is monotonically increasing integers.
    """
    # Ensure float64 for intermediate calculations
    logits = np.asarray(logits, dtype=np.float64)
    vocab_size = len(logits)

    # Stable softmax via log-sum-exp trick
    logits = logits - np.max(logits)  # Numerical stability
    exp_logits = np.exp(logits)
    probs = exp_logits / np.sum(exp_logits)

    # Apply floor probability to guarantee non-zero
    probs = np.maximum(probs, min_prob)
    probs = probs / np.sum(probs)  # Renormalize

    # Convert to integer CDF
    cdf_max = (1 << cdf_precision) - 1
    cdf_float = np.cumsum(probs) * cdf_max
    cdf_int = np.concatenate([[0], np.round(cdf_float[:-1]).astype(np.uint32), [cdf_max]])

    # Enforce strict monotonicity
    for i in range(1, len(cdf_int)):
        if cdf_int[i] <= cdf_int[i - 1]:
            cdf_int[i] = cdf_int[i - 1] + 1

    return cdf_int, cdf_max


def probs_to_cdf(
    probs: np.ndarray, cdf_precision: int = 16, min_prob: float = 1e-8
) -> Tuple[np.ndarray, int]:
    """Convert probability array to CDF with integer precision.

    Args:
        probs: Probability distribution, shape (vocab_size,).
        cdf_precision: Bits of precision for integer CDF.
        min_prob: Minimum probability floor.

    Returns:
        cdf: Cumulative distribution array.
        cdf_max: Maximum CDF value.
    """
    probs = np.asarray(probs, dtype=np.float64)

    # Apply floor
    probs = np.maximum(probs, min_prob)
    probs = probs / np.sum(probs)

    # Convert to integer CDF
    cdf_max = (1 << cdf_precision) - 1
    cdf_float = np.cumsum(probs) * cdf_max
    cdf_int = np.concatenate([[0], np.round(cdf_float[:-1]).astype(np.uint32), [cdf_max]])

    # Enforce strict monotonicity
    for i in range(1, len(cdf_int)):
        if cdf_int[i] <= cdf_int[i - 1]:
            cdf_int[i] = cdf_int[i - 1] + 1

    return cdf_int, cdf_max
