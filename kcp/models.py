"""Model management: pull and locate models locally.

HuggingFace models are downloaded into the local models/ directory for use
with the mem backend. Ollama models are pulled via the ollama CLI for use
with the api backend (they live in ollama's own store at ~/.ollama/models).

models/
  distilgpt2/            ← HF snapshot (config.json, tokenizer, weights, ...)
  meta-llama--Llama-2-7b-hf/
  ...
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Default models directory: <repo_root>/models/
DEFAULT_MODELS_DIR = Path(__file__).parent.parent / "models"


def get_models_dir(models_dir: Optional[str] = None) -> Path:
    """Return the models directory, preferring explicit arg > env var > default."""
    if models_dir:
        return Path(models_dir)
    env_dir = os.environ.get("KCP_MODELS_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_MODELS_DIR


def _hf_local_name(model_id: str) -> str:
    """Convert HF model id (org/name) to safe directory name."""
    return model_id.replace("/", "--")


def resolve_model_path(model_name: str, models_dir: Optional[str] = None) -> str:
    """Resolve a model name to a local path if available, otherwise return as-is.

    Resolution order:
      1. Exact subdirectory match under models_dir.
      2. HF-style slug match (org/name → org--name) under models_dir.
      3. Return model_name unchanged (HF Hub will download on first use).

    Args:
        model_name: HF model id (e.g. "distilgpt2" or "meta-llama/Llama-2-7b-hf")
                    or a raw local path.
        models_dir: Override for the models directory.

    Returns:
        Absolute path string if found locally, else model_name unchanged.
    """
    # Already an absolute path
    p = Path(model_name)
    if p.is_absolute() and p.exists():
        return model_name

    mdir = get_models_dir(models_dir)

    # Exact name match
    candidate = mdir / model_name
    if candidate.exists():
        return str(candidate)

    # HF slug match
    slug_candidate = mdir / _hf_local_name(model_name)
    if slug_candidate.exists():
        return str(slug_candidate)

    return model_name


def pull_hf(
    model_id: str,
    models_dir: Optional[str] = None,
    verbose: bool = False,
) -> Path:
    """Download a HuggingFace model into the local models directory.

    Args:
        model_id: HuggingFace model id, e.g. "distilgpt2".
        models_dir: Override for the models directory.
        verbose: Print progress.

    Returns:
        Path to the downloaded model directory.

    Raises:
        RuntimeError: If huggingface_hub is not installed or download fails.
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        raise RuntimeError(
            "huggingface_hub not installed. Run: pip install huggingface_hub"
        ) from e

    mdir = get_models_dir(models_dir)
    mdir.mkdir(parents=True, exist_ok=True)
    local_dir = mdir / _hf_local_name(model_id)

    if local_dir.exists():
        if verbose:
            print(f"Model already present at {local_dir}")
        return local_dir

    if verbose:
        print(f"Downloading {model_id} → {local_dir}")

    snapshot_download(
        repo_id=model_id,
        local_dir=str(local_dir),
        local_dir_use_symlinks=False,
    )

    if verbose:
        print(f"✓ Saved to {local_dir}")

    return local_dir


def pull_ollama(model_name: str, verbose: bool = False) -> None:
    """Pull a model via the ollama CLI.

    This keeps the model in ollama's own store (~/.ollama/models) for use
    with the api backend. It does not copy files to the local models/ dir.

    Args:
        model_name: Ollama model name, e.g. "llama2" or "mistral:7b".
        verbose: Stream ollama output to stdout.

    Raises:
        RuntimeError: If ollama is not installed or pull fails.
    """
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise RuntimeError(
            "ollama not found. Install from https://ollama.com/download"
        ) from e

    cmd = ["ollama", "pull", model_name]
    if verbose:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
    else:
        result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0:
        stderr = result.stderr.decode() if result.stderr else ""
        raise RuntimeError(f"ollama pull failed:\n{stderr}")

    if verbose:
        print(f"✓ {model_name} ready in ollama store")


def list_local_models(models_dir: Optional[str] = None) -> list:
    """List model directories available in the local models folder.

    Args:
        models_dir: Override for the models directory.

    Returns:
        List of model directory names.
    """
    mdir = get_models_dir(models_dir)
    if not mdir.exists():
        return []
    return sorted(d.name for d in mdir.iterdir() if d.is_dir())


def list_ollama_models() -> list:
    """List models available in the local ollama store.

    Returns:
        List of model name strings, or empty list if ollama not available.
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.strip().splitlines()
        # Skip header row
        return [line.split()[0] for line in lines[1:] if line.strip()]
    except Exception:
        return []
