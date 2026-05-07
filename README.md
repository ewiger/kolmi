# kolmi

Kolmogorov Maximization of (Semantic) Inference


## KCP: Kolmi Compression Program

KCP is a reference implementation of a K-complexity compressor based on autoregressive language models. It provides a CLI for compressing and decompressing text files using either in-memory HuggingFace models or external LLM APIs.

### Quick start
1. Install requirements: `pip install -r requirements-kcp.txt`
2. Pull a model: `kcp.py models pull gpt2` or `./pull_models.sh``
3. Compress a file: `kcp.py compress input.txt` → `input.txt.kcp`
4. Decompress: `kcp.py decompress input.txt.kcp` → `input.txt

More details: [doc/cli/kcp.md](doc/cli/kcp.md) and [doc/compressor/kcp.md](doc/compressor/kcp.md).