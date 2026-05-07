"""API backend for remote/local LLM servers."""

import numpy as np
from typing import Tuple
from kcp.backends.base import Backend
from kcp.config import ApiConfig


class ApiBackend(Backend):
    """LLM API backend (Ollama, OpenAI-compatible, etc.)."""

    def __init__(self, config: ApiConfig):
        """Initialize API backend.

        Args:
            config: ApiConfig with provider and endpoint details.
        """
        self.config = config
        self.vocab_size = None
        self.client = None

    def initialize(self) -> None:
        """Connect to API endpoint and verify capabilities."""
        if self.config.provider == "ollama":
            self._init_ollama()
        elif self.config.provider == "openai":
            self._init_openai()
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")

    def _init_ollama(self) -> None:
        """Initialize Ollama client."""
        try:
            import requests

            # Test connection
            response = requests.get(f"{self.config.api_base}/api/tags", timeout=self.config.timeout)
            if response.status_code != 200:
                raise RuntimeError(f"Ollama server not responding: {response.status_code}")

            if self.config.verbose:
                print(f"Connected to Ollama at {self.config.api_base}")

            # For Ollama, we'll use a standard vocab size (conservative estimate)
            # In production, this would be model-specific
            self.vocab_size = 32000  # Llama-like vocab

        except Exception as e:
            raise RuntimeError(f"Failed to connect to Ollama: {e}") from e

    def _init_openai(self) -> None:
        """Initialize OpenAI-compatible client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base,
            )
            self.vocab_size = 128000  # OpenAI models typically have large vocab

        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

    def get_next_token_logits(self, context_tokens: list) -> np.ndarray:
        """Get logits from API."""
        # Note: Most APIs don't expose raw logits easily
        # This is a placeholder that would need provider-specific implementation
        raise NotImplementedError(
            "API-based logit access not yet implemented. "
            "This would require provider-specific logit extraction (e.g., via raw requests)."
        )

    def get_vocab_size(self) -> int:
        """Return vocabulary size."""
        if self.vocab_size is None:
            raise RuntimeError("Backend not initialized.")
        return self.vocab_size

    def verify_reproducibility(self) -> Tuple[bool, str]:
        """Verify API reproducibility."""
        return (
            False,
            "API backend reproducibility not guaranteed: "
            "provider models may change, latency varies, and logits may not be stable.",
        )
