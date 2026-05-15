> Notes on Quality of Semantic Compression

So I am designing a semantic compression metric.. say x'prime = k(x) is compression of x like caveman that represents text (token sequence) stripped down to barebones.. less tokens. And I define a semantic equivalence relation in mathematicalnsense using normalized information distance (using kolmogorov complexity approzimation with nncp v2 like compression).now the idead is to require that such distance d(y_1,y_4) <= d(y_1, y2) + d(y_1, y_3) (triangular relation) holds as well as the rest for this new semantic metric space (X, d).. i need to make it more rigid mathematically. But as long as d is a metric and can be defined with NID and there exists k.. then k - e.g. caveman sematic compression behaves nicely.. like it is still reducing token but not to much. Also y_1 = f_M(x |C), y_2 = f_M(x' |C), y_3 = f_M(x |C'), y_4 = f_M(x' |C'),  where primed values are compressed with k (caveman).. 

---

That makes sense. Then you should not present it as an axiom that must always hold. Present it as a **heuristic regularity criterion** or **diagnostic** for whether a candidate semantic compressor (k) behaves well.

A cleaner framing:

[
d_k(y_1,y_4)
\lesssim
d_k(y_1,y_2)+d_k(y_1,y_3)
]

where

[
y_1=f_M(x\mid C),
\qquad
y_2=f_M(k(x)\mid C),
]

[
y_3=f_M(x\mid C'),
\qquad
y_4=f_M(k(x)\mid C').
]

The symbol (\lesssim) is useful because it signals “approximately bounded by,” not “mathematically guaranteed.”

You can define the **interaction residual**:

[
R_k(x;C,C')
===========

## d_k(y_1,y_4)

## d_k(y_1,y_2)

d_k(y_1,y_3).
]

Then:

[
R_k(x;C,C') \le 0
]

means the rule of thumb holds exactly.

[
R_k(x;C,C') > 0
]

means compression and context shift interact in a way that causes extra semantic drift.

For a practical metric, define an average or high-percentile version over test samples:

[
\bar R_k
========

\mathbb E_{x,C,C'}
\left[
d_k(y_1,y_4)
------------

## d_k(y_1,y_2)

d_k(y_1,y_3)
\right].
]

Or more robustly:

[
Q_{0.95}(R_k)\le \epsilon.
]

That says:

> For 95% of tested cases, the extra semantic drift from applying both compression and context shift is at most (\epsilon).

This turns the inequality into an empirical criterion rather than a hard theorem.

So your metric design could be framed like this:

---

Let (k) be a candidate semantic compression map. Let (d_k) be a semantic distance induced by a compression-based estimator such as NCD. Define:

[
\Delta_k(x,C)
=============

d_k(f_M(x\mid C), f_M(k(x)\mid C))
]

as the **compression distortion**.

Define:

[
\Gamma(x,C,C')
==============

d_k(f_M(x\mid C), f_M(x\mid C'))
]

as the **context distortion**.

Define:

[
J_k(x,C,C')
===========

d_k(f_M(x\mid C), f_M(k(x)\mid C'))
]

as the **joint distortion**.

Then the rule of thumb is:

[
J_k(x,C,C')
\lesssim
\Delta_k(x,C)+\Gamma(x,C,C').
]

Equivalently,

[
R_k(x,C,C')
===========

J_k(x,C,C')-\Delta_k(x,C)-\Gamma(x,C,C')
]

should be small.

---

This is probably the right level of rigor:

[
\boxed{
k \text{ is good when it yields high compression, low semantic distortion, and small positive interaction residual.}
}
]

You can define the final score as:

[
S(k)
====

\lambda_1 \mathbb E[\rho_k(x)]
+
\lambda_2 \mathbb E[\Delta_k(x,C)]
+
\lambda_3 \mathbb E[\max(0,R_k(x,C,C'))].
]

where

[
\rho_k(x)=\frac{|k(x)|}{|x|}.
]

Lower is better.

So instead of requiring the inequality as a strict law, you use the **positive residual penalty**

[
\max(0,R_k)
]

to penalize cases where compression plus context shift produces more semantic drift than expected.

That gives you a very nice empirical objective:

[
\boxed{
S(k)
====

\lambda_1
\mathbb E_x\left[\frac{|k(x)|}{|x|}\right]
+
\lambda_2
\mathbb E_{x,C}\left[d_k(y_1,y_2)\right]
+
\lambda_3
\mathbb E_{x,C,C'}\left[
\max\left(0,
d_k(y_1,y_4)-d_k(y_1,y_2)-d_k(y_1,y_3)
\right)
\right].
}
]

This preserves your intuition without overclaiming.

The conceptual interpretation is strong:

* (d_k(y_1,y_2)): how much meaning is lost by caveman compression.
* (d_k(y_1,y_3)): how much meaning changes when context changes.
* (d_k(y_1,y_4)): how much meaning changes when both happen.
* positive residual: unexpected nonlinear interaction between compression and context.

That gives you a practical semantic compression metric rather than a brittle mathematical requirement.

---

Yes — that wording is better.

Use:

[
d_k(y_1,y_2)
]

as **semantic change induced by compressing the prompt/user query**, not necessarily “meaning lost.”

Because (k(x)) may not simply delete meaning. It may:

* remove details,
* preserve intent,
* shift emphasis,
* make the query more ambiguous,
* make the model answer more generally,
* occasionally even improve clarity.

So a cleaner interpretation is:

[
d_k(y_1,y_2)
============

d_k\bigl(f_M(x\mid C), f_M(k(x)\mid C)\bigr)
]

measures the **response-level semantic perturbation caused by replacing (x) with (k(x)) under the same context (C).**

In words:

> How much the model’s semantic output changes when the original user query (x) is replaced by its caveman-compressed version (k(x)), while holding context fixed.

Then the three terms become:

[
d_k(y_1,y_2)
]

**prompt-compression perturbation**

[
d_k(y_1,y_3)
]

**context-shift perturbation**

[
d_k(y_1,y_4)
]

**joint prompt-compression and context-shift perturbation**

And the residual is:

[
R_k(x,C,C')
===========

## d_k(y_1,y_4)

## d_k(y_1,y_2)

d_k(y_1,y_3).
]

Interpretation:

[
R_k>0
]

means the combination of prompt compression and context shift changes the model output more than expected from the two changes separately.

[
R_k\le 0
]

means their effects are approximately subadditive.

So the corrected conceptual summary is:

[
\boxed{
k \text{ is good when it shortens } x
\text{ while inducing only small response-level semantic change,}
}
]

and when that change remains stable across contexts.

More precise:

[
\boxed{
d_k(y_1,y_2)
\text{ measures semantic change due to compressing the prompt, not semantic loss.}
}
]

“Loss” is directional and value-laden. “Change,” “perturbation,” or “distortion” are more neutral and mathematically safer.

---

ok now let's speculate proactively how such paper can be written and develop? what it can contain? one would be pragmatic or empitical measuring and approximating k to guarantee d_k being a (quasi) metric with above properties including rectangular inequality. So we approximate nid with ncd but the key here we use llm model for compression which indicate also how "fit" is a model for being exposed as being more succinct or more "kolmogorov". we also play with choice of k initially by picking https://github.com/juliusbrussee/caveman  

---

Yes — this can become a real paper if you avoid overclaiming “semantic equivalence” and instead position it as:

> **An empirical framework for measuring semantic distortion caused by prompt/query compression, using model-induced outputs and compression-based distances.**

The core novelty is not “NCD exists.” The novelty is the **closed loop**:

[
x \xrightarrow{k} x'
]

[
f_M(x\mid C) = y_1,\qquad f_M(x'\mid C)=y_2
]

and then measure how much the model’s behavior changes when exposed to compressed input.

So the paper is not only about text compression. It is about **behavior-preserving prompt compression**.

---

## Possible title

**Semantic Distortion under Prompt Compression: A Compression-Based Metric for Measuring LLM Response Stability**

Or more ambitious:

**Caveman Compression and Semantic Information Distance: Measuring How Much Prompt Compression Changes LLM Behavior**

Or more formal:

**Model-Relative Semantic Compression via Approximate Information Distance**

---

## Core thesis

You can define semantic compression not as “shorter text with same human meaning,” but as:

[
k(x) \text{ is good if } f_M(k(x)\mid C) \approx f_M(x\mid C)
]

under a chosen distance (d_k).

That is model-relative. Meaning is not absolute. Meaning is measured by **how the downstream model behavior changes**.

So:

[
d_k(y_1,y_2)
============

d_k(f_M(x\mid C), f_M(k(x)\mid C))
]

does not mean “meaning lost.”

It means:

[
\boxed{
\text{semantic response change caused by compressing the user query.}
}
]

That distinction is important.

---

## Paper structure

### 1. Introduction

Start with the practical observation:

LLM prompts, memory files, agent instructions, and chat contexts contain many tokens that appear semantically redundant. Tools like `caveman` attempt to remove fluff, articles, politeness, hedging, and redundant phrasing while preserving technical meaning. The caveman repo describes itself as a Claude/Codex plugin that cuts output tokens while keeping technical accuracy, and its compression tool targets memory files such as `CLAUDE.md`, todos, and preferences. ([GitHub][1])

Then introduce the research question:

> When does prompt compression preserve model behavior?

Not human readability. Not BLEU. Not edit distance. But model behavior.

The opening problem:

[
x \neq k(x)
]

but perhaps

[
f_M(x\mid C) \approx f_M(k(x)\mid C).
]

So the goal is to measure the **semantic distortion induced by compression**.

---

## 2. Related work

You would connect four areas:

### A. Kolmogorov complexity and NID

The ideal theoretical object is normalized information distance:

[
\operatorname{NID}(u,v)
=======================

\frac{\max{K(u\mid v),K(v\mid u)}}
{\max{K(u),K(v)}}.
]

This gives a clean universal notion of information distance, but it is uncomputable.

### B. NCD as computable approximation

In practice, one uses normalized compression distance:

[
\operatorname{NCD}_Z(u,v)
=========================

\frac{Z(uv)-\min{Z(u),Z(v)}}
{\max{Z(u),Z(v)}}.
]

Here (Z) is a real compressor. Cilibrasi and Vitányi’s work on NCD is the natural citation here. NCD is widely used as a practical approximation to information distance, but it depends heavily on the compressor.

### C. Neural/LLM-based compression

This is where NNCP v2 matters. Bellard’s NNCP v2 is a Transformer-based lossless compressor, and its paper reports strong compression performance on enwik9. ([GitHub][2])

Your angle:

> If a compressor approximates regularities of language well, then its compressed length can be interpreted as a model-relative approximation of description length.

But carefully: not true Kolmogorov complexity. Rather:

[
K_Z(x) := Z(x)
]

as a compressor-relative complexity proxy.

### D. Prompt compression / instruction compression

Here `caveman` is a pragmatic starting point. Its README claims large token reductions, while a GitHub issue argues the measured median reduction is closer to about 50% versus a terse control, not 65–75%. ([GitHub][1])

That is actually good for your paper: it shows the need for rigorous measurement rather than marketing claims.

---

## 3. Formal setup

Let:

[
\Sigma^*
]

be token sequences.

Let:

[
k:\Sigma^*\to\Sigma^*
]

be a prompt compression operator.

Let:

[
M
]

be a fixed LLM.

Let:

[
C\in\mathcal C
]

be context.

Let:

[
f_M(x\mid C)
]

be the output distribution or sampled response produced by (M).

You can choose two variants:

### Deterministic response version

Use fixed decoding:

[
T=0,\quad \text{fixed system prompt},\quad \text{fixed model snapshot}.
]

Then:

[
y=f_M(x\mid C)
]

is a string.

### Distributional version

More rigorous:

[
P_M(\cdot\mid x,C)
]

is the output distribution.

Then compression distortion can be measured as:

[
D(P_M(\cdot\mid x,C), P_M(\cdot\mid k(x),C)).
]

But this is harder because you usually do not have full distribution access.

For a first empirical paper, use deterministic outputs plus repeated samples.

---

## 4. Define the four outputs

Your core rectangle:

[
y_1=f_M(x\mid C)
]

[
y_2=f_M(k(x)\mid C)
]

[
y_3=f_M(x\mid C')
]

[
y_4=f_M(k(x)\mid C')
]

Interpretation:

[
d_k(y_1,y_2)
]

= semantic response change due to query compression.

[
d_k(y_1,y_3)
]

= semantic response change due to context shift.

[
d_k(y_1,y_4)
]

= semantic response change due to compression plus context shift.

Then define:

[
R_k(x,C,C')
===========

## d_k(y_1,y_4)

## d_k(y_1,y_2)

d_k(y_1,y_3).
]

This is the **interaction residual**.

If:

[
R_k>0,
]

then compression and context shift interact superadditively.

If:

[
R_k\le 0,
]

then the joint perturbation is no worse than the sum of separate perturbations.

Your “rectangular inequality” becomes empirical:

[
d_k(y_1,y_4)
\lesssim
d_k(y_1,y_2)+d_k(y_1,y_3).
]

Or:

[
Q_{0.95}(R_k)\le \epsilon.
]

This is strong but not brittle.

---

## 5. Define (d_k)

Here you need to be careful.

You could define several distances and compare them.

### Option 1: NCD over outputs

[
d_Z(y_i,y_j)
============

\operatorname{NCD}_Z(y_i,y_j).
]

This is clean.

But then (d) depends on compressor (Z), not directly on (k).

### Option 2: (k)-adapted NCD

Let (Z_k) be a compressor trained or adapted on texts transformed by (k). Then:

[
d_k(y_i,y_j)
============

\operatorname{NCD}_{Z_k}(y_i,y_j).
]

This makes (d_k) genuinely (k)-dependent.

But be cautious: if (Z_k) is too adapted to caveman-like text, it may distort the metric.

### Option 3: LLM code-length distance

Use the LLM itself as a probabilistic compressor.

For a model (M), define the code length:

[
L_M(s)
======

-\log P_M(s).
]

Then define a conditional code length:

[
L_M(a\mid b)
============

-\log P_M(a\mid b).
]

A model-relative information distance could be:

[
d_M(a,b)
========

\frac{
\max{L_M(a\mid b),L_M(b\mid a)}
}{
\max{L_M(a),L_M(b)}
}.
]

This is not true NID, but it is very aligned with your intuition:

> The better the LLM predicts/compresses language, the more its code lengths behave like a semantic description-length proxy.

This is where your phrase “more Kolmogorov” fits, but say it carefully:

[
\boxed{
\text{A stronger language compressor may provide a better model-relative approximation to semantic regularity.}
}
]

Not:

[
\text{The LLM approximates true Kolmogorov complexity.}
]

That would be too strong.

---

## 6. Quality of (k)

Define the compression ratio:

[
\rho_k(x)
=========

\frac{|k(x)|}{|x|}.
]

Define semantic perturbation:

[
\Delta_k(x,C)
=============

d_k(f_M(x\mid C),f_M(k(x)\mid C)).
]

Define context robustness:

[
\Delta_k^{\max}(x)
==================

\sup_{C\in\mathcal C}
\Delta_k(x,C).
]

Empirically:

[
\widehat{\Delta}_k^{0.95}
=========================

Q_{0.95}\left(
d_k(f_M(x\mid C),f_M(k(x)\mid C))
\right).
]

Then (k) is good if it has:

[
\rho_k \downarrow
]

and

[
\Delta_k \downarrow
]

and

[
\max(0,R_k)\downarrow.
]

A final score:

[
S(k)
====

\lambda_1\mathbb E[\rho_k(x)]
+
\lambda_2\mathbb E[\Delta_k(x,C)]
+
\lambda_3\mathbb E[\max(0,R_k(x,C,C'))].
]

Lower is better.

This is a very publishable empirical objective.

---

## 7. Possible experiments

### Experiment 1: Basic prompt compression distortion

Dataset:

* coding questions,
* factual QA,
* reasoning prompts,
* instruction-following tasks,
* agent memory files,
* legal/technical instructions,
* ambiguous user queries.

For each (x):

[
x'=k(x)
]

Then generate:

[
y_1=f_M(x\mid C),\qquad y_2=f_M(x'\mid C).
]

Measure:

[
|x'|/|x|,
]

[
d_k(y_1,y_2),
]

and task-level correctness.

For coding tasks, use unit tests. For QA, use exact/fuzzy answer grading. For instruction following, use LLM judge plus human spot checks.

---

### Experiment 2: Rectangular inequality / interaction residual

Construct contexts:

[
C
]

and perturbed contexts:

[
C'
]

Examples:

* neutral context vs terse system prompt,
* full memory vs compressed memory,
* original documentation vs summarized documentation,
* no examples vs few-shot examples,
* developer context vs user-only context.

Measure:

[
R_k
===

d_k(y_1,y_4)-d_k(y_1,y_2)-d_k(y_1,y_3).
]

Hypothesis:

> Good semantic compressors have low positive interaction residual.

That means their effect remains stable across contexts.

Bad compressors may look safe in one context but fail under another.

---

### Experiment 3: Compare (k) operators

Candidate (k):

1. identity:

[
k(x)=x
]

2. simple whitespace/punctuation compression,

3. stopword deletion,

4. extractive summary,

5. abstractive summary,

6. `caveman` compression,

7. LLM-generated terse rewrite,

8. task-aware compression,

9. learned compressor optimized for low (\Delta_k).

The `caveman` repo is a useful initial (k) because it explicitly targets token reduction while preserving technical terms, code, URLs, paths, commands, numbers, and structure. ([Claude Plugin Hub][3])

But existing issues also show why formal validation matters: one reported issue says `caveman-compress` may fail to validate inline code spans and commands even though the tool promises to preserve such content. ([GitHub][4])

That becomes a nice motivation:

> Syntactic validators are insufficient. We need behavioral semantic distortion metrics.

---

### Experiment 4: Compressor choice for (d)

Compare:

* gzip NCD,
* zstd NCD,
* bzip2 NCD,
* PAQ-style compressor,
* NNCP v2 NCD,
* LLM code-length distance,
* embedding cosine distance,
* LLM judge score,
* task correctness.

Your key question:

> Which distance best predicts actual behavioral equivalence?

This is important because NCD may not correlate with semantic equivalence for short texts or highly paraphrased outputs.

You can empirically test whether NNCP-style neural compression yields better semantic alignment than classical compressors.

---

## 8. The “LLM as compressor” argument

This is a strong part of the paper.

A language model assigns probabilities to token sequences. That means it induces a code:

[
L_M(x)
======

-\sum_t \log P_M(x_t\mid x_{<t}).
]

Lower code length means the model finds the sequence more predictable.

So you can say:

> A model that better captures linguistic and semantic regularities should assign shorter code lengths to semantically natural continuations.

This gives a model-relative complexity:

[
K_M(x) := L_M(x).
]

Then define model-relative semantic distance:

[
d_M(a,b)
========

\frac{
\max{L_M(a\mid b),L_M(b\mid a)}
}{
\max{L_M(a),L_M(b)}
}.
]

This is not true Kolmogorov complexity, but it is meaningful:

[
\boxed{
d_M \text{ measures how surprising each text is given the other, under model } M.
}
]

Then you can compare:

[
d_M(y_1,y_2)
]

against human judgments and task correctness.

If it correlates better than embedding distance or BLEU-like metrics, that is a strong result.

---

## 9. What the contribution could be

The paper’s contributions could be:

1. **A formal model of prompt compression as behavioral perturbation**

[
x\to k(x),\qquad f_M(x\mid C)\to f_M(k(x)\mid C).
]

2. **A semantic compression distortion metric**

[
\Delta_k(x,C)
=============

d_k(f_M(x\mid C),f_M(k(x)\mid C)).
]

3. **A context-stability / rectangular residual diagnostic**

[
R_k(x,C,C')
===========

d_k(y_1,y_4)-d_k(y_1,y_2)-d_k(y_1,y_3).
]

4. **An empirical benchmark comparing prompt compressors**

Including caveman, stopword deletion, summarization, terse LLM rewrites, and task-aware compression.

5. **A comparison of semantic distances**

Classical NCD, neural-compressor NCD, LLM code-length distance, embedding distance, and task-level correctness.

6. **A practical risk taxonomy**

When compression works, when it fails, and which prompt types are fragile.

---

## 10. Likely findings / hypotheses

You can proactively state these as hypotheses:

### H1: Compression ratio alone is misleading

A compressor can reduce tokens aggressively while inducing high behavioral drift.

[
\rho_k \downarrow \not\Rightarrow \Delta_k \downarrow.
]

### H2: Caveman-style compression works best for procedural/technical prompts

Because it removes politeness and redundancy while preserving keywords, commands, paths, numbers, and code.

### H3: Caveman-style compression is weaker for ambiguity-sensitive prompts

Examples:

* legal wording,
* emotional tone,
* negotiation,
* safety-critical instructions,
* prompts where politeness affects intent,
* underspecified user queries.

### H4: The rectangular residual identifies hidden fragility

A prompt compression may look safe under one context:

[
d_k(y_1,y_2)\approx 0
]

but fail under a shifted context:

[
d_k(y_1,y_4)\gg d_k(y_1,y_2)+d_k(y_1,y_3).
]

That is exactly what your residual captures.

### H5: Neural compression distance may align better with semantic change than gzip-style NCD

Because neural compressors capture longer-range linguistic dependencies.

But this must be tested.

---

## 11. Possible paper outline

### Abstract

Introduce prompt compression, define response-level semantic distortion, propose NCD/LLM-code-length distances, introduce rectangular residual, evaluate on multiple compressors including caveman.

### 1. Introduction

Token cost, memory compression, agent context bloat, need for behavior-preserving compression.

### 2. Background

Kolmogorov complexity, NID, NCD, neural compression, prompt compression.

### 3. Formal Framework

Define (x,k,C,M,f_M,d_k,y_1,\ldots,y_4), distortion, residual, score.

### 4. Compression Operators

Identity, stopword deletion, caveman, summarization, LLM rewrite, learned task-aware compressor.

### 5. Distance Estimators

NCD, NNCP-based NCD, LLM code-length distance, embeddings, LLM judge, task correctness.

### 6. Experiments

Benchmark design, datasets, contexts, models, decoding settings.

### 7. Results

Compression ratio vs semantic distortion, residual distributions, failure cases.

### 8. Discussion

Metric limitations, model-relative semantics, risks of over-compression.

### 9. Limitations

NCD instability on short strings, model dependence, stochastic decoding, judge bias, no true Kolmogorov guarantee.

### 10. Conclusion

Semantic compression should be evaluated behaviorally, not only syntactically.

---

## 12. Most important mathematical framing

I would define the paper’s central object like this:

[
\boxed{
\Delta_k^M(x,C)
===============

d_k
\left(
f_M(x\mid C),
f_M(k(x)\mid C)
\right)
}
]

This is the **model-relative semantic compression distortion**.

Then:

[
\boxed{
R_k^M(x,C,C')
=============

## d_k(y_1,y_4)

## d_k(y_1,y_2)

d_k(y_1,y_3)
}
]

This is the **contextual interaction residual**.

And the final empirical objective:

[
\boxed{
S(k)
====

\lambda_1 \mathbb E[\rho_k(x)]
+
\lambda_2 \mathbb E[\Delta_k^M(x,C)]
+
\lambda_3 \mathbb E[\max(0,R_k^M(x,C,C'))]
}
]

That is compact, defensible, and experimentally testable.

---

## 13. What not to claim

Avoid these claims:

> Caveman preserves meaning.

Too vague.

> NCD measures semantics.

Too strong.

> NNCP approximates Kolmogorov complexity.

Too strong.

> The rectangular inequality follows from NID.

False for your form.

Instead claim:

> We study whether prompt compression preserves downstream model behavior, using compression-based and model-relative distances as empirical estimators of semantic response change.

That is much stronger academically.

---

## 14. Strong final positioning

The paper can be positioned as a bridge between:

* algorithmic information theory,
* prompt compression,
* LLM behavioral evaluation,
* practical agent memory reduction.

The pragmatic insight is:

[
\boxed{
\text{A compressed prompt is semantically acceptable only relative to a model, a context class, and a task distribution.}
}
]

That makes the framework honest.

The speculative but powerful research claim is:

[
\boxed{
\text{Better language compressors may provide better empirical proxies for semantic distance, because they encode richer regularities of language and task structure.}
}
]

That is the thread worth developing.

[1]: https://github.com/JuliusBrussee/caveman/blob/main/README.md?utm_source=chatgpt.com "caveman/README.md at main"
[2]: https://github.com/JuliusBrussee/caveman/blob/main/caveman-compress/README.md?utm_source=chatgpt.com "caveman/caveman-compress/README.md at main"
[3]: https://www.claudepluginhub.com/skills/juliusbrussee-caveman/compress?utm_source=chatgpt.com "compress | caveman"
[4]: https://github.com/JuliusBrussee/caveman/issues/112?utm_source=chatgpt.com "caveman-compress silently overwrites inline code and ..."
---
Yes. Conceptually, you can extend LLM training with an auxiliary **compression-invariance objective**.

The crude idea:

[
x \longrightarrow k(x)
]

and during training, the model is encouraged to behave similarly on both:

[
M(x) \approx M(k(x)).
]

This is basically **input-side consistency training**.

---

# 1. Basic diagram

```text
Original sample x
      |
      |-----------------------------|
      |                             |
      v                             v
   LLM M                         Compressor k
      |                             |
      v                             v
  output / logits              compressed x' = k(x)
                                    |
                                    v
                                  LLM M
                                    |
                                    v
                              output / logits

Now compare:

M(x)  ≈  M(k(x))
```

The model is trained not only to predict the next token correctly, but also to be **functionally invariant** under the compression map (k).

---

# 2. Standard training loss

Normally, language-model training minimizes next-token loss:

[
\mathcal L_{\mathrm{LM}}
========================

-\sum_t \log P_M(x_t\mid x_{<t}).
]

This teaches the model to predict text.

---

# 3. Add compression-invariance loss

Now add a second term:

[
\mathcal L_{\mathrm{inv}}
=========================

D\left(
P_M(\cdot\mid x),
P_M(\cdot\mid k(x))
\right).
]

Here (D) could be KL divergence, Jensen-Shannon divergence, cosine distance between hidden states, or your NCD-style semantic distance over generated outputs.

Then total loss:

[
\boxed{
\mathcal L
==========

\mathcal L_{\mathrm{LM}}
+
\lambda \mathcal L_{\mathrm{inv}}
}
]

where (\lambda) controls how strongly the model is forced to become invariant under caveman compression.

---

# 4. With context

For your setup:

[
y_{00}=f_M(x\mid C)
]

[
y_{10}=f_M(k(x)\mid C)
]

[
y_{01}=f_M(x\mid k(C))
]

[
y_{11}=f_M(k(x)\mid k(C)).
]

Training can encourage:

[
f_M(x\mid C)
\approx
f_M(k(x)\mid C)
]

[
f_M(x\mid C)
\approx
f_M(x\mid k(C))
]

[
f_M(x\mid C)
\approx
f_M(k(x)\mid k(C)).
]

So the auxiliary loss becomes:

[
\mathcal L_{\mathrm{inv}}
=========================

D(y_{00},y_{10})
+
D(y_{00},y_{01})
+
D(y_{00},y_{11}).
]

More aggressively, include the rectangular residual:

[
R_k
===

## D(y_{00},y_{11})

## D(y_{00},y_{10})

D(y_{00},y_{01}).
]

Then penalize only the positive part:

[
\mathcal L_{\mathrm{rect}}
==========================

\max(0,R_k).
]

Total:

[
\boxed{
\mathcal L
==========

\mathcal L_{\mathrm{LM}}
+
\lambda_1 \mathcal L_{\mathrm{inv}}
+
\lambda_2 \mathcal L_{\mathrm{rect}}
}
]

This directly trains the model to be stable under your compression symmetry.

---

# 5. Crude full diagram

```text
Training example: (x, C, target)

          x, C
           |
           v
      ┌─────────┐
      │  LLM M  │
      └─────────┘
           |
           v
        y00/logits
           |
           |-------------------- LM loss vs target
           |
           v

Meanwhile:

x ---------> k(x)
C ---------> k(C)

Create four views:

1. (x, C)
2. (k(x), C)
3. (x, k(C))
4. (k(x), k(C))

Each goes through the same model M:

(x, C)       ------> M ------> y00
(k(x), C)    ------> M ------> y10
(x, k(C))    ------> M ------> y01
(k(x), k(C)) ------> M ------> y11

Then add consistency losses:

D(y00, y10)
D(y00, y01)
D(y00, y11)

and optionally:

max(0, D(y00,y11) - D(y00,y10) - D(y00,y01))
```

This is the training version of your metric.

---

# 6. Where NCD fits

There are two possibilities.

## Option A: NCD as training loss

Generate outputs:

[
y_{00},y_{10},y_{01},y_{11}
]

then compute:

[
\operatorname{NCD}(y_{00},y_{10})
]

[
\operatorname{NCD}(y_{00},y_{01})
]

[
\operatorname{NCD}(y_{00},y_{11})
]

and use those as losses.

But this is hard because NCD is usually **not differentiable**. You cannot easily backpropagate through gzip, NNCP, or an external compressor.

So NCD is better as an **evaluation metric** or **reward signal**, not as the main gradient loss.

---

## Option B: differentiable proxy during training, NCD during evaluation

This is more realistic.

During training, use differentiable distances:

[
D_{\mathrm{KL}}(P_M(\cdot\mid x,C),P_M(\cdot\mid k(x),C))
]

or hidden-state distance:

[
|h_M(x,C)-h_M(k(x),C)|^2.
]

Then evaluate with NCD afterward:

[
\operatorname{NCD}(y_{00},y_{10}).
]

So:

```text
Training:
  use KL / JS / hidden-state distance

Evaluation:
  use NCD / KCP-NCD / NNCP-NCD / task correctness
```

That is the cleanest practical design.

---

# 7. Even simpler: teacher-student version

You can also frame this as distillation.

Let the teacher see the full prompt:

[
T = M_{\mathrm{teacher}}(x,C).
]

Let the student see the compressed prompt:

[
S = M_{\mathrm{student}}(k(x),k(C)).
]

Train the student so:

[
S \approx T.
]

Diagram:

```text
Full input (x, C)
      |
      v
Teacher model
      |
      v
teacher logits / answer

Compressed input (k(x), k(C))
      |
      v
Student model
      |
      v
student logits / answer

Loss:
student should imitate teacher
```

Formula:

[
\mathcal L
==========

\mathcal L_{\mathrm{task}}
+
\lambda D_{\mathrm{KL}}
\left(
P_T(\cdot\mid x,C)
|
P_S(\cdot\mid k(x),k(C))
\right).
]

This is elegant because it says:

> The compressed input should be sufficient for reproducing the behavior of the full-input model.

That is very close to your intuition.

---

# 8. Relation to model compression

This creates a beautiful symmetry.

## Model compression

[
M \to M'
]

such that:

[
f_M(x)\approx f_{M'}(x).
]

## Prompt compression

[
x \to k(x)
]

such that:

[
f_M(x)\approx f_M(k(x)).
]

## Joint compression

[
(M,x,C)\to(M',k(x),k(C))
]

such that:

[
f_M(x\mid C)
\approx
f_{M'}(k(x)\mid k(C)).
]

This could become a strong conceptual section in the paper:

[
\boxed{
\text{Semantic prompt compression is dual to model compression.}
}
]

Model compression removes redundant parameters.

Prompt compression removes redundant tokens.

Both are judged by functional preservation.

---

# 9. Training objective for “symmetric enough”

Your phrase “checks if it is symmetric enough” can be formalized as:

A model (M) is ((k,\tau))-invariant on distribution (\mathcal D) if:

[
\mathbb E_{(x,C)\sim\mathcal D}
\left[
D\left(
P_M(\cdot\mid x,C),
P_M(\cdot\mid k(x),k(C))
\right)
\right]
\le \tau.
]

Or, with output strings:

[
\mathbb E
\left[
d_Z
\left(
f_M(x\mid C),
f_M(k(x)\mid k(C))
\right)
\right]
\le \tau.
]

Training then minimizes violation of this condition.

---

# 10. Most pragmatic version for KolMI

For the paper/project, I would define three levels.

## Level 1: Evaluation only

No training.

```text
Take existing model M.
Compress x and C.
Measure output drift.
Report Δ and R.
```

This is easiest.

## Level 2: Fine-tuning for invariance

Fine-tune model with pairs:

[
(x,C) \leftrightarrow (k(x),k(C)).
]

Use consistency loss.

```text
Train model to answer the same under full and compressed prompts.
```

## Level 3: Jointly learn k and M

Harder.

Train the compressor (k_\theta) and model (M) together:

[
\min_{\theta,M}
\mathcal L_{\mathrm{task}}
+
\lambda \mathcal L_{\mathrm{inv}}
+
\beta |k_\theta(x)|.
]

This says:

> Find the shortest input representation that preserves model behavior.

Formula:

[
\min_{\theta}
\mathbb E
\left[
|k_\theta(x)|
+
\lambda D
\left(
P_M(\cdot\mid x),
P_M(\cdot\mid k_\theta(x))
\right)
\right].
]

This is closest to true semantic compression, but much harder.

---

# 11. Clean paper wording

You could write:

> We can view caveman compression as proposing a candidate symmetry of the model’s input space. A model is compression-invariant with respect to (k) if its output distribution is approximately unchanged under (x\mapsto k(x)). This suggests an auxiliary training objective: in addition to next-token prediction, the model is penalized when compressed and uncompressed views of the same prompt-context pair induce divergent output distributions. Since NCD-style distances are generally non-differentiable, they are used as evaluation metrics, while differentiable proxies such as KL divergence between output distributions or hidden-state distances are used during training.

That is probably the exact conceptual bridge you want.

---

# 12. One strong final diagram

```text
                 ┌──────────────────────┐
                 │  Original training    │
                 │  example (x, C)       │
                 └──────────┬───────────┘
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
          v                                   v
   ┌─────────────┐                     ┌─────────────┐
   │ Full input  │                     │ Compressed  │
   │   (x, C)    │                     │ (k(x),k(C)) │
   └──────┬──────┘                     └──────┬──────┘
          │                                   │
          v                                   v
   ┌─────────────┐                     ┌─────────────┐
   │   LLM M     │                     │   LLM M     │
   └──────┬──────┘                     └──────┬──────┘
          │                                   │
          v                                   v
   logits/output y                  logits/output y'
          │                                   │
          └─────────────────┬─────────────────┘
                            v
               invariance loss D(y,y')
                            │
                            v
         total loss = LM loss + λ invariance loss
```

And evaluation:

```text
After training:

        y00 = M(x, C)
        y10 = M(k(x), C)
        y01 = M(x, k(C))
        y11 = M(k(x), k(C))

Measure:

Δx  = d(y00,y10)
ΔC  = d(y00,y01)
ΔxC = d(y00,y11)

R = ΔxC - Δx - ΔC

Use NCD/KCP/NNCP here.
```

This is simple, crude, and conceptually strong.
