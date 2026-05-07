# KCP: Architecture and Compression Approach

> Spec: [KIP-0001](../proposals/accepted/KIP-0001-compressor/README.md) | Reference: [NNCP](nncp.md) | CLI guide: [doc/cli/kcp.md](../cli/kcp.md)

LLM-assisted text compression using token-level logit probabilities fed into an arithmetic encoder. Designed for two distinct use-cases: Kolmogorov complexity approximation (NID / semantic similarity) and portable file archiving.

## Core Idea

A language model assigns a probability distribution over the next token given a context. High-probability tokens need fewer bits to encode; low-probability ones need more. KCP exploits this directly: for each token in a text it queries the model for logits, converts them to a deterministic integer CDF, and encodes the token's position in that distribution using an arithmetic code. Decompression is symmetric — the same model and config must be used, making the compressed representation tied to the model.

Because the bitstream is fully determined by (model, config) with no randomness, `K(x) ≈ len(compress(x))` is a valid approximation of Kolmogorov complexity for any fixed model.

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  CLI Layer  (kcp.py)                                    │
│  File-oriented commands: compress, decompress, info     │
│  Always uses the archive layer for file I/O             │
├─────────────────────────────────────────────────────────┤
│  Archive Layer  (kcp/format.py, kcp/library.py)         │
│  archive_compress() / archive_decompress()              │
│  Wraps core output with KCP\x01 header + JSON           │
│  metadata + blake2b-256 checksum                        │
├─────────────────────────────────────────────────────────┤
│  Core Layer  (kcp/core.py, kcp/coder/, kcp/probability) │
│  compress_text() / decompress_text()                    │
│  Raw bitstream, no headers — use for NID / K-complexity │
└─────────────────────────────────────────────────────────┘
```

The separation matters: the core layer's output is a pure function of (text, config). That property makes it suitable for K-complexity approximation and NID — no format overhead, no timestamps, same bytes every time given the same model.

## Compression Pipeline

`KCPCompressor` in `kcp/core.py` drives the encode/decode loop.

**Compression:**
1. Tokenize input text with the model's tokenizer.
2. For each token (with a sliding context window of up to `context_size` previous tokens):
   - Query backend → logits over full vocabulary.
   - `logits_to_cdf()` — stable softmax → floor probability → monotone integer CDF (`cdf_precision` bits).
   - Arithmetic-encode the token using its CDF range.
3. Encode EOS as terminator.
4. Return raw bit sequence as bytes.

**Decompression:**
1. Initialize arithmetic decoder with the bitstream.
2. Repeatedly: query backend for logits → rebuild CDF → decode next symbol.
3. Stop at EOS. Detokenize → original text.

The codec lives in `kcp/coder/arithmetic.py`. Each symbol is encoded at its CDF low-value using `cdf_precision` bits — a simplified but fully deterministic and correct scheme (not full interval arithmetic coding).

## Backends

### MemBackend (`kcp/backends/mem_backend.py`)

Loads a HuggingFace causal-LM and tokenizer in-process with `transformers` + `torch`.

- **Deterministic**: same hardware + dtype → same logits → same bitstream.
- Model resolution (see below) checks the local `models/` cache first.
- Supports `device`: `cpu`, `cuda`, `mps`.

### ApiBackend (`kcp/backends/api_backend.py`)

Queries an external LLM API (Ollama, OpenAI-compatible) for logits.

- **Experimental**: reproducibility is not guaranteed across API calls or server restarts.
- Logit extraction depends on the provider supporting per-token log-probability output.

## Model Resolution (`kcp/models.py`)

When `MemBackend` initializes, it calls `resolve_model_path(model_name, models_dir)` before loading. Resolution order:

1. **Absolute path** — used as-is if it exists on disk.
2. **`models/<model_name>/`** — local cache directory checked first.
3. **`models/<org>--<name>/`** — HF-style slug (e.g. `meta-llama/Llama-2-7b-hf` → `meta-llama--Llama-2-7b-hf`).
4. **HF Hub fallback** — `model_name` returned unchanged; `transformers` downloads to `~/.cache/huggingface/hub/` on first use.

This is why compression works even with an empty `models/` folder: `distilgpt2` falls through to the HF Hub path and is cached by `transformers` for subsequent runs.

| Location | How to populate | Used by |
|---|---|---|
| `models/<name>/` | `kcp.py models pull <id>` | MemBackend, offline / pinned use |
| `~/.cache/huggingface/hub/` | automatic on first compress | transformers, transparent |
| `~/.ollama/models/` | `kcp.py models pull <name> --source ollama` | ApiBackend |

Override the models directory with `--models-dir <path>` or `KCP_MODELS_DIR` env var.

## Library API

### Core Layer — for NID / K-complexity

```python
from kcp import compress_text, decompress_text
from kcp.config import MemConfig

config = MemConfig(model_path="distilgpt2", context_size=256, cdf_precision=16)

bitstream = compress_text("Hello, world!", config)   # raw bytes, no header
recovered = decompress_text(bitstream, config)        # config must match exactly
```

> Both sides must use **exactly the same config** (model, context_size, cdf_precision, eos_token_id). There is no self-describing header at this layer.

### Archive Layer — for portable storage

```python
from kcp import archive_compress, archive_decompress
from kcp.config import MemConfig

config = MemConfig(model_path="distilgpt2")

archive_bytes = archive_compress("My text", config)          # bytes with header
text = archive_decompress(archive_bytes)                      # config read from header
archive_compress("My text", config, output_path="data.kcp")  # write to file
text = archive_decompress("data.kcp")                        # read from file
```

### NID Example

```python
from kcp import compress_text
from kcp.config import MemConfig

def nid(text_a, text_b, config):
    K_x  = len(compress_text(text_a, config))
    K_y  = len(compress_text(text_b, config))
    K_xy = len(compress_text(text_a + text_b, config))
    return (K_xy - min(K_x, K_y)) / max(K_x, K_y)

config = MemConfig(model_path="distilgpt2")
print(nid("fox jumps", "dog jumps", config))
```

## Archive File Format

Produced by `kcp/format.py`:

```
Offset   Len   Field
──────────────────────────────────────────────────────────────
0        4     Magic: b'KCP\x01'
4        1     Version: 0x01
5        1     Mode: 0x00 = mem, 0x01 = api
6        4     Metadata size (little-endian uint32)
10       N     Metadata JSON (mode, config, cdf_precision, ...)
10+N     32    Checksum: blake2b-256 of payload
10+N+32  …     Raw bitstream (core layer output)
```

The checksum covers only the raw bitstream payload. `read_archive()` raises `ValueError("Checksum mismatch")` on corruption.

## Configuration Reference

### MemConfig

```python
MemConfig(
    model_path="distilgpt2",   # HF model id or local path
    tokenizer_path=None,        # defaults to model_path
    device="cpu",               # cpu | cuda | mps
    dtype="float32",            # float32 | float16
    models_dir=None,            # overrides models/ root (or KCP_MODELS_DIR)
    context_size=256,           # sliding token window
    cdf_precision=16,           # CDF bits (16–24)
    eos_token_id=2,             # terminator token
    verbose=False,
)
```

### ApiConfig

```python
ApiConfig(
    provider="ollama",                   # ollama | openai
    api_base="http://localhost:11434",
    api_key=None,                        # or env KCP_API_KEY
    api_model="llama2",
    timeout=30.0,
    max_retries=3,
    context_size=256,
    cdf_precision=16,
    eos_token_id=2,
)
```

## Testing

```bash
python3 -m pytest tests/kcp -q
```

## Known Limitations (v0.1)

1. **Arithmetic coder**: Simplified deterministic implementation (not full arithmetic coding)
2. **API backend**: Logit extraction not fully implemented (would need provider-specific APIs)
3. **Reproducibility**: Float precision varies across hardware; exact bit-perfect decode not guaranteed for `api` mode
4. **Speed**: Slower than gzip/zstd (inherent to token-level encoding with per-token inference)

## Performance Notes

- Compression speed: ~1-10 tokens/sec (depends on model size and device)
- Decompression speed: Similar to compression
- Archive overhead: ~200-500 bytes for metadata + checksum
- Best suited for: text similarity analysis (NID), research, archival (not production compression)

## Future Work

- [ ] Optimize arithmetic coder for better compression ratios
- [ ] Implement proper logit extraction for API backends
- [ ] Add byte-level mode for non-text data
- [ ] Multi-token context caching for speed
- [ ] Quantized model support for smaller footprint
- [ ] Batch compression for multiple texts

## References

- Original NNCP v2: https://github.com/fire/pytorch-nncp
- Bellard ts_zip: https://bellard.org/ts_zip/
- Arithmetic coding: https://en.wikipedia.org/wiki/Arithmetic_coding

## License

MIT (matching NNCP v2)
