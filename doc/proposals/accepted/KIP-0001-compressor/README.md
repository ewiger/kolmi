# KIP-0001: KCP LLM-Assisted Text Compressor

Status: Accepted  
Date: 2026-05-07  
Owner: Yauhen Yakimovich

## 1. Summary

This KIP proposes `kcp.py`, a Python compressor/decompressor for text that uses
LLM next-token probabilities (logits) as the statistical model for arithmetic
coding.

The tool must support two execution modes:

1. `mem`: run a local model loaded in memory as a binary, similar to NNCP v2
	flow (see [doc/compressor/nncp.md](../../../compressor/nncp.md)).
2. `api`: query an LLM API (local or remote, for example Ollama local server,
	OpenAI-compatible endpoints, or similar) to obtain logits/probabilities.

Implementation documentation: [doc/compressor/kcp.md](../../../compressor/kcp.md).

In all other respects (model-driven probability estimation, deterministic
encode/decode flow, range coding behavior, and stream format discipline), NNCP
v2 is the reference recipe.

## 2. Goals

1. Build a working end-to-end compressor/decompressor script: `kcp.py`.
2. Provide both `mem` and `api` backend modes behind one CLI.
3. Use `typer` for the CLI interface.
4. Expose a reusable Python library API that works with text strings directly
	(not only files).
5. Keep implementation structure close to NNCP v2 for easier validation and
	iteration (in python).

## 3. Non-Goals

1. Competing with gzip/zstd speed in v1.
2. Training new models in this KIP.
3. Supporting arbitrary binary input in v1 (text-first scope).
4. Guaranteeing cross-platform bit-identical decode for all backends in v1
	(tracked as a risk and follow-up).

## 4. Terminology

1. Token: model vocabulary symbol.
2. Logits: raw model scores for next token.
3. PMF/CDF: probability mass and cumulative distribution converted to integer
	form for arithmetic coding.
4. Backend: provider used to get next-token logits (`mem` or `api`).

## 5. High-Level Design

`kcp.py` performs token-level lossless compression:

1. Tokenize input text.
2. For each position, query backend for next-token logits given prior context.
3. Convert logits to deterministic integer CDF.
4. Arithmetic-encode the observed token.
5. Persist metadata required for decompression.

Decompression mirrors the process:

1. Read metadata/header.
2. Reconstruct backend configuration.
3. For each token step, request logits for current context.
4. Decode one token from arithmetic stream via same CDF mapping.
5. Detokenize decoded tokens to recover original text.

Critical requirement: encoder and decoder must produce equivalent CDFs per step
for the same context.

## 6. Architecture

Suggested module layout (can be adjusted, but responsibilities should remain):

1. `kcp.py`
	- Typer entrypoint and command wiring.
2. `kcp/core.py`
	- Main compress/decompress orchestration.
3. `kcp/backends/base.py`
	- Backend protocol/interface.
4. `kcp/backends/mem_backend.py`
	- Local in-memory model backend.
5. `kcp/backends/api_backend.py`
	- Remote/local API backend abstraction.
6. `kcp/coder/arithmetic.py`
	- Arithmetic/range encoder and decoder.
7. `kcp/probability.py`
	- Logits -> stable integer CDF mapping.
8. `kcp/format.py`
	- Container header and metadata read/write.
9. `kcp/library.py`
	- String-based library functions.

## 7. Backend Modes

### 7.1 `mem` Mode

`mem` mode loads model + tokenizer directly in process memory and performs
logit inference locally.

Requirements:

1. Deterministic inference switches where available.
2. Explicit model/tokenizer identity in output metadata.
3. Configurable context window and temperature behavior (default deterministic,
	no sampling).
4. No stochastic decoding logic.

Implementation guidance:

1. Follow NNCP v2 flow as close recipe for iterative next-token probability
	production.
2. Keep logits handling numeric path stable (float -> integer CDF).

### 7.2 `api` Mode

`api` mode obtains next-token logits/probabilities from an API endpoint.

Requirements:

1. Provider abstraction that supports:
	- local server (for example Ollama),
	- remote providers (for example ChatGPT-compatible APIs),
	- pluggable custom endpoint.
2. Endpoint capability check at startup: verify logits/probabilities are
	available and stable enough for decode.
3. Metadata must store provider + model identifier + API-relevant parameters.
4. Fail fast if backend cannot guarantee decompression reproducibility.

Important note:

API providers may change model behavior over time. If reproducibility cannot be
ensured, archives should be marked as non-portable/experimental.

## 8. CLI Specification (Typer)

CLI is implemented using `typer` with two primary commands and shared options.

### 8.1 Commands

1. `kcp compress`
	- Compress text file into `.kcp` output.
2. `kcp decompress`
	- Decompress `.kcp` archive back to text.

### 8.2 Common Arguments

1. `--mode [mem|api]`
	- Backend mode.
2. `--input, -i PATH`
	- Input file path.
3. `--output, -o PATH`
	- Output file path.
4. `--encoding TEXT` (default: `utf-8`)
	- Text file encoding.
5. `--context-size INT`
	- Max context tokens for backend calls.
6. `--cdf-precision INT` (default: `16`)
	- Integer CDF precision bits.
7. `--eos-token TEXT|INT` (optional)
	- End marker override.
8. `--verbose`
	- Progress and backend diagnostics.

### 8.3 `mem`-Specific Arguments

1. `--model-path PATH`
2. `--tokenizer-path PATH` (optional if bundled)
3. `--device TEXT` (for example `cpu`, `cuda`)
4. `--dtype TEXT` (for example `float32`, `float16`)

### 8.4 `api`-Specific Arguments

1. `--provider TEXT` (for example `ollama`, `openai`, `custom`)
2. `--api-base URL`
3. `--api-key TEXT|ENV`
4. `--api-model TEXT`
5. `--timeout FLOAT`
6. `--max-retries INT`

### 8.5 Optional Utility Commands

1. `kcp inspect`
	- Print archive metadata and compatibility hints.
2. `kcp check-backend`
	- Validate backend reproducibility capability before compression.

## 9. Layered API Architecture

To support both **Kolmogorov complexity approximation (NID)** and **portable file storage**,
the implementation uses a three-layer design:

### 9.1 Core Compression Layer (Raw Bitstream)

Low-level functions that produce **raw compressed data without headers or metadata**.
These functions enable using KCP for approximating normalized information distance via
Kolmogorov complexity: `K(x|y) ≈ len(compress(x || y))`.

**Minimum API surface:**

```python
def compress_text(text: str, config: CompressorConfig) -> bytes:
    """Compress text to raw bitstream (no header). Backend/config must be deterministic."""
    ...

def decompress_text(bitstream: bytes, config: DecompressorConfig) -> str:
    """Decompress raw bitstream. Config must match the encoder's settings exactly."""
    ...
```

**Design constraints:**

1. No header, magic bytes, or versioning; output is pure compressed data.
2. Decoder **requires explicit config** (backend, model, tokenizer, CDF precision, EOS)—cannot infer from bitstream.
3. Determinism is caller's responsibility: config must match encoder perfectly.
4. Suitable for approximating K-complexity, NID, and other information-theoretic measurements.

### 9.2 Archive Format Layer (With Metadata)

High-level wrapper that adds headers, versioning, and environment metadata for **portable
file storage and reproducibility**.

**API surface:**

```python
def archive_compress(text: str, config: CompressorConfig, output_path: str | None = None) -> bytes:
    """Compress text and wrap in archive format with headers and metadata.
    Returns bytes if output_path is None, else writes to file and returns size info."""
    ...

def archive_decompress(archive_bytes: bytes | str, input_path: str | None = None, config_override: dict | None = None) -> str:
    """Decompress archive format. Extracts metadata; uses override if provided.
    Can accept either raw bytes or a file path."""
    ...
```

**Archive structure:**

1. Magic bytes (e.g., `b'KCP\x01'`).
2. Version.
3. Mode (`mem` or `api`).
4. Model/tokenizer/provider metadata + hash.
5. Numeric coding params (CDF precision, EOS id, context size).
6. Optional integrity checksum (blake3 hash of raw bitstream).
7. Raw compressed bitstream (from core layer).

**Metadata should be sufficient to:**

- Fail early if environment is incompatible.
- Store backend/model identifiers for reproducibility checks.
- Enable `inspect` command to show archive contents.

### 9.3 CLI Layer

Wraps archive format for user-facing file operations. Uses `compress`/`decompress`
commands that implicitly use archive format.

## 10. Library API Design Detail

**Design constraints across layers:**

1. Core and archive layers share the same low-level compression logic (no duplication).
2. Archive layer wraps core layer by adding header I/O.
3. CLI layer uses archive layer exclusively for file operations.
4. Exceptions are typed and actionable across all layers.

**For NID/K-complexity use cases:**

- Use core layer (`compress_text` / `decompress_text`) directly.
- Pass explicit config to both encoder and decoder.
- Verify determinism by round-tripping small test inputs.
- Measure compressed size ratios to approximate K(x|y).

## 11. Archive Format Implementation Details

The archive format is a **zip-like container** that separates metadata from payload:

```
[Magic 4 bytes: 'KCP\x01']
[Version 1 byte]
[Mode 1 byte: 0x00 = mem, 0x01 = api]
[Metadata size: 4 bytes (little-endian)]
[Metadata JSON or binary dict]
  - model_id / tokenizer_id (mem) or provider + api_model (api)
  - context_size
  - cdf_precision
  - eos_token_id
  - backend_config_hash (for reproducibility checks)
  - timestamp (optional)
[Checksum 32 bytes: blake3(raw_bitstream)]
[Raw bitstream payload]
```

**Implementation approach:**

1. Core layer produces raw bitstream.
2. Archive wrapper reads/writes metadata around it.
3. On decompress: extract metadata, pass to decoder, then decompress payload.
4. For NID use: skip archive layer and use core layer directly.

## 12. Determinism and Correctness

Required checks:

1. Round-trip identity: `decompress(compress(text)) == text`.
2. Deterministic CDF conversion from logits.
3. Non-zero floor probability per token before normalization.
4. Reject decode when backend metadata mismatches archive requirements.

Known risk areas:

1. Floating-point drift across hardware/software stacks.
2. API model upgrades changing logits.
3. Tokenizer version drift.

## 13. Testing Strategy

1. Unit tests:
	- arithmetic coder invariants,
	- logits -> CDF conversion,
	- header parsing/serialization.
2. Integration tests:
	- `mem` compress/decompress round-trips (core layer),
	- `api` mock provider round-trips (core layer),
	- archive round-trips (full archive layer).
3. Golden tests:
	- fixed model/config expected bitstream snapshots for NID validation (where feasible).
4. CLI tests:
	- `compress`/`decompress` arg handling and error messages (archive layer).
5. NID sanity tests:
	- verify K(x|y) approximation properties on small test strings.

## 14. Implementation Plan

1. Implement core arithmetic coder + deterministic CDF conversion (core layer).
2. Implement backend interface and `mem` backend.
3. Implement core library API: `compress_text()`, `decompress_text()` (no headers).
4. Implement archive wrapper: `archive_compress()`, `archive_decompress()` (with metadata).
5. Implement Typer CLI using archive layer (`compress`, `decompress`, optional `inspect`).
6. Add `api` backend with provider adapters.
7. Add tests: unit, integration, golden, NID sanity checks.
8. Document usage examples for both core (NID) and archive (portable storage) use cases.

## 15. Acceptance Criteria

1. `kcp.py` exists and runs with Typer CLI.
2. Both modes are implemented: `mem` and `api`.
3. Common CLI file arguments exist for input/output (archive layer).
4. Core library functions support text string compression/decompression **without headers**.
5. Archive layer wraps core layer and adds metadata.
6. NNCP v2-inspired workflow is reflected in architecture and coding path.
7. Basic test suite passes for deterministic round-trip on supported setup.
8. NID sanity test passes: `len(compress(x||y)) <= len(compress(x)) + len(compress(y))` (approximately).

## 16. Open Questions

1. Should v1 freeze one tokenizer/model pair to reduce portability issues?
2. Should `api` mode be marked experimental until reproducibility policy is
	formalized?
3. Do we want optional byte-level mode after text-first milestone?
4. Should archive metadata include a "reproducibility level" tag (e.g., "full", "api-drift-risk")?

## 17. References and Use Cases

### Use Case 1: Normalized Information Distance (NID)

For research on algorithmic similarity:

```python
from kcp import compress_text
from kcp.config import MemConfig

# Use deterministic mem backend
config = MemConfig(model_path="...", cdf_precision=16)

# K-complexity approximations
K_x = len(compress_text("text A", config))
K_y = len(compress_text("text B", config))
K_xy = len(compress_text("text Atext B", config))

# Normalized information distance
NID = (K_xy - min(K_x, K_y)) / max(K_x, K_y)
```

### Use Case 2: Portable File Storage

For sharing compressed archives:

```python
from kcp import archive_compress, archive_decompress
from kcp.config import MemConfig

config = MemConfig(model_path="...")
archive_bytes = archive_compress("My text here", config)

# Archive includes metadata; decoder can check compatibility
recovered_text = archive_decompress(archive_bytes)
assert recovered_text == "My text here"
```
