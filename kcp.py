#!/usr/bin/env python3
"""KCP (Kolmi Compressor) CLI using Typer.

See doc/compressor/kcp.md for full design and usage documentation.
"""

import typer
from enum import Enum
from pathlib import Path
from typing import Optional

from kcp.config import MemConfig, ApiConfig
from kcp.library import archive_compress, archive_decompress
from kcp.format import read_archive

app = typer.Typer(
    help="KCP: LLM-Assisted Text Compressor",
    no_args_is_help=True,
)

models_app = typer.Typer(help="Manage local models for KCP compression.")
app.add_typer(models_app, name="models")


class Mode(str, Enum):
    mem = "mem"
    api = "api"


# ---------------------------------------------------------------------------
# compress
# ---------------------------------------------------------------------------

@app.command()
def compress(
    input_file: Path = typer.Argument(..., help="Input text file to compress"),
    output_file: Optional[Path] = typer.Argument(None, help="Output .kcp archive (default: <input>.kcp)"),
    mode: Mode = typer.Option(Mode.mem, "--mode", "-m", help="Backend: mem (local model) or api"),
    context_size: int = typer.Option(256, "--context-size", help="Token context window"),
    cdf_precision: int = typer.Option(16, "--cdf-precision", help="CDF integer precision (bits)"),
    eos_token_id: int = typer.Option(2, "--eos-token-id", help="End-of-sequence token ID"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    # mem-specific
    model: Optional[str] = typer.Option(None, "--model", help="[mem] Model name or path (resolved from models/)"),
    models_dir: Optional[Path] = typer.Option(None, "--models-dir", help="[mem] Local models directory"),
    tokenizer: Optional[str] = typer.Option(None, "--tokenizer", help="[mem] Tokenizer path (default: same as model)"),
    device: str = typer.Option("cpu", "--device", help="[mem] Inference device: cpu, cuda, mps"),
    dtype: str = typer.Option("float32", "--dtype", help="[mem] Weight dtype: float32 or float16"),
    # api-specific
    provider: str = typer.Option("ollama", "--provider", help="[api] Provider: ollama or openai"),
    api_base: str = typer.Option("http://localhost:11434", "--api-base", help="[api] API base URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="KCP_API_KEY", help="[api] API key"),
    api_model: str = typer.Option("llama2", "--api-model", help="[api] Model name on the server"),
    timeout: float = typer.Option(30.0, "--timeout", help="[api] Request timeout (seconds)"),
    max_retries: int = typer.Option(3, "--max-retries", help="[api] Max retries on failure"),
):
    """Compress a text file into a KCP archive."""
    if not input_file.exists():
        typer.echo(f"Error: input file not found: {input_file}", err=True)
        raise typer.Exit(1)

    out = output_file or input_file.with_suffix(".kcp")
    text = input_file.read_text(encoding="utf-8")
    if verbose:
        typer.echo(f"Input: {input_file} ({len(text):,} chars)")

    if mode == Mode.mem:
        config = MemConfig(
            model_path=model or "distilgpt2",
            tokenizer_path=tokenizer,
            device=device,
            dtype=dtype,
            models_dir=str(models_dir) if models_dir else None,
            context_size=context_size,
            cdf_precision=cdf_precision,
            eos_token_id=eos_token_id,
            verbose=verbose,
        )
    else:
        config = ApiConfig(
            provider=provider,
            api_base=api_base,
            api_key=api_key,
            api_model=api_model,
            timeout=timeout,
            max_retries=max_retries,
            context_size=context_size,
            cdf_precision=cdf_precision,
            eos_token_id=eos_token_id,
            verbose=verbose,
        )

    try:
        archive_bytes = archive_compress(text, config, output_path=str(out))
    except Exception as e:
        typer.echo(f"Error during compression: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)

    ratio = len(archive_bytes) / max(len(text), 1)
    typer.echo(
        f"✓  {input_file}  →  {out}\n"
        f"   original {len(text):,} chars  |  archive {len(archive_bytes):,} bytes  |  ratio {ratio:.2%}"
    )


# ---------------------------------------------------------------------------
# decompress
# ---------------------------------------------------------------------------

@app.command()
def decompress(
    input_file: Path = typer.Argument(..., help="KCP archive to decompress"),
    output_file: Optional[Path] = typer.Argument(None, help="Output text file (default: <input>.txt)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Decompress a KCP archive back to text."""
    if not input_file.exists():
        typer.echo(f"Error: input file not found: {input_file}", err=True)
        raise typer.Exit(1)

    out = output_file or input_file.with_suffix(".txt")

    try:
        text = archive_decompress(str(input_file))
    except Exception as e:
        typer.echo(f"Error during decompression: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)

    out.write_text(text, encoding="utf-8")
    typer.echo(f"✓  {input_file}  →  {out}  ({len(text):,} chars)")


# ---------------------------------------------------------------------------
# info / inspect
# ---------------------------------------------------------------------------

def _print_archive_info(input_file: Path, archive_size: int, raw_bitstream: bytes, metadata: dict, mode: str) -> None:
    """Render a human-readable summary of archive metadata and compression settings."""
    cfg = metadata.get("config", {})
    model = cfg.get("model_path") or cfg.get("api_model", "?")
    provider = cfg.get("provider", "-") if mode == "api" else "-"

    typer.echo(f"Archive  : {input_file}")
    typer.echo(f"Format   : KCP v1")
    typer.echo(f"Size     : {archive_size:,} bytes")
    typer.echo(f"Payload  : {len(raw_bitstream):,} bytes")
    typer.echo(f"Mode     : {mode}")
    typer.echo(f"Model    : {model}")
    typer.echo(f"Provider : {provider}")
    typer.echo(f"Context  : {metadata.get('context_size', '?')} tokens")
    typer.echo(f"CDF      : {metadata.get('cdf_precision', '?')} bits")
    typer.echo(f"EOS      : {metadata.get('eos_token_id', '?')}")
    typer.echo("Checksum : blake2b-256 (verified)")
    if "config_hash" in cfg:
        typer.echo(f"CfgHash  : {cfg['config_hash']}")


@app.command("info")
@app.command("inspect")
def info(
    input_file: Path = typer.Argument(..., help="KCP archive to inspect"),
):
    """Scan a .kcp archive header and report how it was compressed."""
    if not input_file.exists():
        typer.echo(f"Error: file not found: {input_file}", err=True)
        raise typer.Exit(1)

    try:
        data = input_file.read_bytes()
        raw_bitstream, metadata, mode = read_archive(data)
    except Exception as e:
        typer.echo(f"Error reading archive: {e}", err=True)
        raise typer.Exit(1)

    _print_archive_info(input_file, len(data), raw_bitstream, metadata, mode)


# ---------------------------------------------------------------------------
# models pull
# ---------------------------------------------------------------------------

@models_app.command("pull")
def models_pull(
    model_id: str = typer.Argument(..., help="Model to pull (HF id or ollama name)"),
    source: str = typer.Option("hf", "--source", "-s", help="Source: hf (HuggingFace) or ollama"),
    models_dir: Optional[Path] = typer.Option(None, "--models-dir", help="Local models directory override"),
    verbose: bool = typer.Option(True, "--verbose/--quiet", help="Show download progress"),
):
    """Pull a model locally.

    HuggingFace models are saved under models/<model-id>/ and used by the mem backend.
    Ollama models are pulled into the ollama store and used by the api backend.

    Examples:

      kcp.py models pull distilgpt2

      kcp.py models pull meta-llama/Llama-2-7b-hf

      kcp.py models pull llama2 --source ollama
    """
    from kcp.models import pull_hf, pull_ollama

    if source == "hf":
        try:
            local_dir = pull_hf(
                model_id,
                models_dir=str(models_dir) if models_dir else None,
                verbose=verbose,
            )
            typer.echo(f"✓  Saved to {local_dir}")
            typer.echo(f"   Use with: kcp.py compress <file> --model {model_id}")
        except RuntimeError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)

    elif source == "ollama":
        try:
            pull_ollama(model_id, verbose=verbose)
            typer.echo(f"✓  '{model_id}' ready in ollama store")
            typer.echo(f"   Use with: kcp.py compress <file> --mode api --api-model {model_id}")
        except RuntimeError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)

    else:
        typer.echo(f"Unknown source '{source}'. Use 'hf' or 'ollama'.", err=True)
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# models list
# ---------------------------------------------------------------------------

@models_app.command("list")
def models_list(
    models_dir: Optional[Path] = typer.Option(None, "--models-dir", help="Local models directory override"),
    show_ollama: bool = typer.Option(False, "--ollama", help="Also list ollama-managed models"),
):
    """List locally available models."""
    from kcp.models import list_local_models, list_ollama_models, get_models_dir

    mdir = get_models_dir(str(models_dir) if models_dir else None)
    local = list_local_models(str(models_dir) if models_dir else None)

    typer.echo(f"Local models  ({mdir}):")
    if local:
        for name in local:
            typer.echo(f"  {name}")
    else:
        typer.echo("  (none — run: kcp.py models pull <model_id>)")

    if show_ollama:
        typer.echo("\nOllama models:")
        ollama = list_ollama_models()
        if ollama:
            for name in ollama:
                typer.echo(f"  {name}")
        else:
            typer.echo("  (none or ollama not running)")


if __name__ == "__main__":
    app()
