
> what is nncp? how does it relate to ts_zip?

Bellard’s `ts_zip` does roughly this: tokenize text losslessly, have encoder and decoder run the same language model, use the model’s next-token probabilities, then arithmetic-code the actual next token. It uses a built-in deterministic RWKV 169M v4 model; Bellard notes GPU is needed for reasonable speed, about 4 GB RAM, and up to ~1 MB/s on RTX 4090. ([bellard.org][1])

Difficulty by level:

| Goal                                      | Difficulty | Why                                                                                                                                    |
| ----------------------------------------- | ---------: | -------------------------------------------------------------------------------------------------------------------------------------- |
| Toy proof-of-concept                      |   **3/10** | Use Hugging Face logits + simple range coder over tokens.                                                                              |
| Lossless decompressor that works reliably |   **6/10** | Encoder/decoder must produce bit-identical token probabilities.                                                                        |
| Competitive compressor                    | **8–9/10** | Needs deterministic inference, quantized CDFs, fast KV-cache decoding, file format, tokenizer edge cases, and performance engineering. |
| Bellard-quality implementation            |  **9+/10** | His value is mostly engineering discipline, not just “LLM + arithmetic coding.”                                                        |

The core algorithm is conceptually simple:

```text
compress:
  state = LLM initial state
  for token in tokenize(text):
      probs = LLM.predict_next(state)
      arithmetic_encode(token, probs)
      state = LLM.update(state, token)

decompress:
  state = LLM initial state
  while not end:
      probs = LLM.predict_next(state)
      token = arithmetic_decode(probs)
      output token
      state = LLM.update(state, token)
```

The catch: **lossless means the decoder must reproduce exactly the same probability table**. That is where most Python prototypes fail. Floating-point nondeterminism, GPU kernels, different library versions, tokenizer ambiguity, softmax rounding, and CDF quantization can all corrupt decompression.

A practical Python prototype should avoid “raw floating probabilities” and instead:

1. Use a fixed tokenizer and store its version/config.
2. Use a local model, not an API LLM.
3. Run deterministic inference, ideally CPU first.
4. Convert logits to an integer CDF, e.g. 16–24 bit precision.
5. Guarantee every token has nonzero probability.
6. Store model ID, tokenizer ID, coder precision, and end marker in the archive.
7. Test by round-tripping tiny files before optimizing.

Minimal stack:

```text
Python
torch or llama.cpp bindings
transformers or tokenizers
custom arithmetic/range coder
integer CDF from logits
```

The biggest performance issue is that compression and decompression both require **one model inference per token**. That is inherently slow compared with gzip/zstd/xz. Bellard’s page explicitly notes it is much slower than conventional compressors. ([bellard.org][1])

My estimate: you could build a working educational version in **a weekend to a week**. A reliable, portable, reasonably fast version is more like **several weeks**. A compressor that competes with `ts_zip` is a serious systems/ML project.

[1]: https://bellard.org/ts_zip/?utm_source=chatgpt.com "ts_zip: Text Compression using Large Language Models"

---

> what other compression related stuff does he did with cnn?

He mainly did **NNCP**: *Lossless Data Compression with Neural Networks*.

Despite your “CNN” wording, Bellard’s compressor was not convolutional-CNN based. It used:

* **LSTM models** in the first version
* later **Transformer models**
* arithmetic coding driven by neural next-byte / next-symbol probabilities
* his own C tensor library, **LibNC**, for speed

NNCP is the direct predecessor/spiritual ancestor of `ts_zip`: same broad idea — neural model predicts probabilities, arithmetic coder encodes the actual stream — but NNCP was more general data/text compression, while `ts_zip` is specifically LLM-based text compression. ([Bellard][1])

Other compression-related Bellard projects:

* **LZEXE** — old executable compressor from 1989.
* **BPG** — Better Portable Graphics, an image format based on HEVC intra coding.
* **NNCP** — neural lossless compressor.
* **ts_zip** — LLM-based text compressor.
* **TSAC** — very-low-bitrate audio compression utility. ([Wikipedia][2])

So the relevant “neural compression before `ts_zip`” project is **NNCP**, not really CNN-based compression.

[1]: https://bellard.org/nncp/?utm_source=chatgpt.com "NNCP: Lossless Data Compression with Neural Networks"
[2]: https://en.wikipedia.org/wiki/Fabrice_Bellard?utm_source=chatgpt.com "Fabrice Bellard"


---

> does nncp has any python code? I remember I saw smth like this

Yes — you probably saw **NNCP v2**, which *does* include Python code.

Bellard released an older version called:

> **NNCP v2 (Python + PyTorch, GPU required)**

on the NNCP page. ([Bellard][1])

The newer NNCP versions are mostly C/LibNC-based, but the older Transformer version is Python/PyTorch and is exactly the kind of thing you’d want to study for building an LLM/arithmetic-coding compressor.

The Python version contains:

* `nncp.py`
* Transformer-XL style model
* arithmetic coder
* preprocessing pipeline
* deterministic-ish compression logic

There’s also a GitHub mirror:

* [fire/pytorch-nncp](https://github.com/fire/pytorch-nncp?utm_source=chatgpt.com)

The README explicitly says:

> “NNCP v2 is a lossless data compressor based on the Transformer model.” ([GitHub][2])

And importantly:

> `nncp.py` was tested with Python + PyTorch + CUDA. ([GitHub][2])

This is probably what you remember.

What makes it especially valuable for learning:

* it is relatively small/simple compared to modern LLM infra,
* it directly connects Transformer logits → arithmetic coding,
* it demonstrates deterministic compression/decompression constraints,
* it avoids the huge complexity of full GPT inference stacks.

One especially interesting detail:
Bellard notes that this Python/PyTorch version is **not portable across machines** because floating-point behavior differs:

> “compressed output cannot usually be decompressed on a different machine.” ([GitHub][2])

That exact issue is why `ts_zip` later moved toward much more carefully controlled deterministic inference.

If your goal is:

> “I want to understand how neural probability models integrate with arithmetic coding”

then NNCP v2 is honestly one of the best educational codebases available. Much easier to digest than modern LLM-serving stacks.

[1]: https://bellard.org/nncp/?utm_source=chatgpt.com "NNCP: Lossless Data Compression with Neural Networks"
[2]: https://github.com/fire/pytorch-nncp?utm_source=chatgpt.com "fire/pytorch-nncp"


--
> is nncp v2 opensource?

Yes — NNCP v2 is effectively open source.

Bellard released the Python/PyTorch version as source code under the:

> **MIT license**

The GitHub mirror includes the MIT license file and the full Python implementation. ([github.com](https://github.com/fire/pytorch-nncp?utm_source=chatgpt.com))

So unlike `ts_zip`, NNCP v2 is much closer to a normal open-source project:

* source available,
* permissive license,
* modifiable/reusable,
* easy to experiment with.

The main implementation files are small enough to realistically study:

* Transformer model
* arithmetic/range coding
* training/inference loop
* compression/decompression pipeline

That makes it a very good starting point if you want to:

* understand neural entropy coding,
* build your own LLM compressor,
* replace the Transformer with a modern small LLM,
* experiment with token-level vs byte-level coding.

Architecturally, NNCP v2 is basically:

```text
input bytes
   ↓
Transformer predicts next-symbol probabilities
   ↓
range/arithmetic coder encodes actual symbol
   ↓
compressed bitstream
```

which is the same core idea later scaled up in `ts_zip`.
