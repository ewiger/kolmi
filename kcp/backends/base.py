"""Backend interface for obtaining next-token logits."""

from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np


class Backend(ABC):
    """Abstract backend for token probability prediction."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize backend (load models, connect to API, etc.)."""
        pass

    @abstractmethod
    def get_next_token_logits(self, context_tokens: list) -> np.ndarray:
        """Get logits for next token given context.

        Args:
            context_tokens: List of token IDs (context).

        Returns:
            Logits array of shape (vocab_size,).
        """
        pass

    @abstractmethod
    def get_vocab_size(self) -> int:
        """Return vocabulary size."""
        pass

    @abstractmethod
    def verify_reproducibility(self) -> Tuple[bool, str]:
        """Verify backend can produce reproducible outputs.

        Returns:
            (success: bool, message: str)
        """
        pass
