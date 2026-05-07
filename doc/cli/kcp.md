# KCP CLI Reference

> Architecture and compression approach: [doc/compressor/kcp.md](../compressor/kcp.md)

`kcp.py` is the command-line interface for KCP. It always uses the archive layer, so every output file is a self-describing `.kcp` archive with embedded metadata and a blake2b checksum.

## Installation

```bash
pip install -r requirements-kcp.txt   # or: uv pip install -r requirements-kcp.txt
```

Requirements installed: `typer`, `transformers`, `torch`, `numpy`, `accelerate`, `huggingface_hub`, `requests`.

## Command Overview

```
kcp.py [OPTIONS] COMMAND [ARGS]...

Commands:
  compress    Compress a text file into a KCP archive
  decompress  Decompress a KCP archive back to text
  info        Scan a .kcp archive header and report how it was compressed
  inspect     Alias for info
  models      Manage local models
    pull        Pull a model from HuggingFace Hub or ollama
    list        List locally available models
```

---

## compress

```
kcp.py compress INPUT_FILE [OUTPUT_FILE] [OPTIONS]
```

Compress a UTF-8 text file into a `.kcp` archive. If `OUTPUT_FILE` is omitted the archive is written to `<INPUT_FILE>.kcp`.

### Options

**Shared:**

| Option | Default | Description |
|---|---|---|
| `--mode`, `-m` | `mem` | Backend: `mem` (local model) or `api` |
| `--context-size` | `256` | Sliding token context window |
| `--cdf-precision` | `16` | CDF integer precision in bits (16–24) |
| `--eos-token-id` | `2` | End-of-sequence token ID |
| `--verbose`, `-v` | off | Print progress details |

**mem backend:**

| Option | Default | Description |
|---|---|---|
| `--model` | `distilgpt2` | HF model id or name in `models/` |
| `--models-dir` | *(see below)* | Local models directory override |
| `--tokenizer` | same as `--model` | Tokenizer path override |
| `--device` | `cpu` | `cpu`, `cuda`, or `mps` |
| `--dtype` | `float32` | `float32` or `float16` |

**api backend:**

| Option | Default | Description |
|---|---|---|
| `--provider` | `ollama` | `ollama` or `openai` |
| `--api-base` | `http://localhost:11434` | API endpoint URL |
| `--api-key` | — | API key (`KCP_API_KEY` env var also accepted) |
| `--api-model` | `llama2` | Model name on the server |
| `--timeout` | `30.0` | Per-request timeout (seconds) |
| `--max-retries` | `3` | Retry attempts on failure |

### Examples

```bash
# Basic — downloads distilgpt2 from HF Hub on first run
kcp.py compress essay.txt

# Explicit output path
kcp.py compress essay.txt essay.kcp

# Use a locally pulled model
kcp.py compress essay.txt --model distilgpt2

# GPU, smaller dtype
kcp.py compress essay.txt --model mistralai/Mistral-7B-v0.1 --device cuda --dtype float16

# API backend (Ollama running locally)
kcp.py compress essay.txt --mode api --api-model llama2
```

---

## decompress

```
kcp.py decompress INPUT_FILE [OUTPUT_FILE]
```

Decompress a `.kcp` archive. Config is read from the archive header — no flags needed. Output defaults to `<INPUT_FILE>.txt`.

```bash
kcp.py decompress essay.kcp
kcp.py decompress essay.kcp recovered.txt
```

---

## info / inspect

```
kcp.py info INPUT_FILE
kcp.py inspect INPUT_FILE   # alias
```

Read and display the archive header without decompressing. Verifies the blake2b checksum and reports:

```
Archive  : essay.kcp
Format   : KCP v1
Size     : 407 bytes
Payload  : 90 bytes
Mode     : mem
Model    : distilgpt2
Provider : -
Context  : 256 tokens
CDF      : 16 bits
EOS      : 2
Checksum : blake2b-256 (verified)
CfgHash  : cef68b13d6ae2293...
```

---

## models pull

```
kcp.py models pull MODEL_ID [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--source`, `-s` | `hf` | `hf` (HuggingFace Hub) or `ollama` |
| `--models-dir` | *(see below)* | Save location override |
| `--verbose` / `--quiet` | verbose | Show download progress |

**HuggingFace models** are saved under `models/<model-id>/` (slashes replaced with `--`) and used by the `mem` backend.

**Ollama models** are pulled into the ollama store (`~/.ollama/models/`) and used by the `api` backend.

```bash
# Pull into models/ (for mem backend)
kcp.py models pull distilgpt2
kcp.py models pull meta-llama/Llama-2-7b-hf

# Pull into ollama (for api backend)
kcp.py models pull llama2 --source ollama

# Custom cache location
kcp.py models pull distilgpt2 --models-dir /data/kcp-models
```

---

## models list

```
kcp.py models list [OPTIONS]
```

| Option | Default | Description |
|---|---|---|
| `--models-dir` | *(see below)* | Directory to scan |
| `--ollama` | off | Also list ollama-managed models |

```bash
kcp.py models list
kcp.py models list --ollama
```

---

## Model Resolution

When the `mem` backend initializes, it resolves the `--model` value in this order:

1. Absolute path on disk — used as-is.
2. `models/<name>/` — local explicit cache (populated by `models pull`).
3. `models/<org>--<name>/` — HF slug style.
4. HF Hub fallback — `transformers` downloads to `~/.cache/huggingface/hub/` on first use, then reuses the cache.

**An empty `models/` folder is fine.** `compress` will download the model automatically on first use. Use `models pull` only when you need offline access, version pinning, or a custom save location.

### models/ directory

Default: `<repo_root>/models/` (ignored by `.gitignore`).

Override (in priority order):
1. `--models-dir <path>` flag
2. `KCP_MODELS_DIR` environment variable
3. Default repo-relative path

---

## Environment Variables

| Variable | Description |
|---|---|
| `KCP_MODELS_DIR` | Override the local models directory |
| `KCP_API_KEY` | API key for `--mode api` (same as `--api-key`) |
| `HF_TOKEN` | HuggingFace token for authenticated Hub access and higher rate limits |
