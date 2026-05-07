"""In-memory model backend."""

import numpy as np
from typing import Tuple, Optional
from kcp.backends.base import Backend
from kcp.config import MemConfig
from kcp.models import resolve_model_path


class MemBackend(Backend):
    """In-memory LLM backend using transformers/torch."""

    def __init__(self, config: MemConfig):
        """Initialize memory backend.

        Args:
            config: MemConfig with model and tokenizer paths.
        """
        self.config = config
        self.model = None
        self.tokenizer = None
        self.vocab_size = None

    def initialize(self) -> None:
        """Load model and tokenizer."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            # Resolve model path: check local models/ dir first, then HF Hub
            model_path = resolve_model_path(
                self.config.model_path, self.config.models_dir
            )
            if self.config.verbose:
                if model_path != self.config.model_path:
                    print(f"Resolved model '{self.config.model_path}' → {model_path}")
                else:
                    print(f"Loading model from {model_path}")

            # Load tokenizer
            tokenizer_path = resolve_model_path(
                self.config.tokenizer_path or self.config.model_path,
                self.config.models_dir,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

            # Load model
            torch_dtype = torch.float32 if self.config.dtype == "float32" else torch.float16
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map=self.config.device,
                torch_dtype=torch_dtype,
            )
            self.model.eval()

            # Get vocab size
            self.vocab_size = self.model.config.vocab_size

            if self.config.verbose:
                print(f"Model loaded. Vocab size: {self.vocab_size}")

        except ImportError as e:
            raise RuntimeError(
                "transformers/torch not installed. Install with: pip install transformers torch"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}") from e

    def get_next_token_logits(self, context_tokens: list) -> np.ndarray:
        """Get logits for next token.

        Args:
            context_tokens: List of token IDs.

        Returns:
            Logits array, shape (vocab_size,).
        """
        if self.model is None:
            raise RuntimeError("Backend not initialized. Call initialize() first.")

        import torch

        # Truncate to context size
        context = context_tokens[-(self.config.context_size) :]
        input_ids = torch.tensor([context], dtype=torch.long, device=self.model.device)

        with torch.no_grad():
            outputs = self.model(input_ids)
            logits = outputs.logits[0, -1, :]  # Last token logits

        return logits.cpu().numpy().astype(np.float64)

    def get_vocab_size(self) -> int:
        """Return vocabulary size."""
        if self.vocab_size is None:
            raise RuntimeError("Backend not initialized.")
        return self.vocab_size

    def verify_reproducibility(self) -> Tuple[bool, str]:
        """Verify reproducibility on test context."""
        try:
            # Test with simple context
            test_tokens = [self.tokenizer.bos_token_id or 0]
            logits1 = self.get_next_token_logits(test_tokens)
            logits2 = self.get_next_token_logits(test_tokens)

            # Check if identical
            if np.allclose(logits1, logits2, rtol=1e-6):
                return True, "Reproducibility OK: consecutive calls produce identical logits."
            else:
                return False, "Warning: logits differ between consecutive calls (possible stochastic behavior)."

        except Exception as e:
            return False, f"Reproducibility check failed: {e}"
