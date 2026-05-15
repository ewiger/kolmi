> summarize what we can do experimentally with caveman. don't forget the tau - tolerance to defined the equivalence relation .. explain why caveman is a great example of when semantic coherence may break... and entropy may rise


Here is the experimental program around **caveman compression**.

## Core idea

Use `caveman` as a concrete compression operator:

[
k(x)=x'
]

where (x') is a shorter, stripped-down version of the original prompt/query/context.

Then test whether a fixed model (M) behaves approximately the same under:

[
(x,C)
\quad \text{vs.} \quad
(k(x),C),
]

[
(x,k(C)),
\quad \text{and} \quad
(k(x),k(C)).
]

So the main question is not:

> Did caveman preserve human-readable meaning?

but rather:

> Did caveman preserve the model’s functional behavior?

Formally:

[
f_M(x\mid C) \approx f_M(k(x)\mid C).
]

---

## Four experimental outputs

Define:

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

Interpretation:

[
y_{00}
]

is the baseline answer.

[
y_{10}
]

tests **query compression**.

[
y_{01}
]

tests **context compression**.

[
y_{11}
]

tests **joint query/context compression**.

Then measure distances:

[
\Delta_X=d(y_{00},y_{10})
]

semantic response change due to compressing the user query.

[
\Delta_C=d(y_{00},y_{01})
]

semantic response change due to compressing the context.

[
\Delta_{XC}=d(y_{00},y_{11})
]

semantic response change due to compressing both.

---

## The (\tau)-tolerance equivalence relation

You need a tolerance threshold:

[
\tau > 0.
]

Then define approximate semantic equivalence as:

[
y_i \sim_\tau y_j
\quad \Longleftrightarrow \quad
d(y_i,y_j)\le \tau.
]

So:

[
y_{00}\sim_\tau y_{10}
]

means:

> Compressing the query did not change the model’s answer beyond the allowed tolerance.

Similarly:

[
y_{00}\sim_\tau y_{01}
]

means:

> Compressing the context did not change the answer beyond tolerance.

And:

[
y_{00}\sim_\tau y_{11}
]

means:

> Joint compression of query and context is still behaviorally acceptable.

Strictly, for (\tau>0), this is not always a perfect mathematical equivalence relation because transitivity can fail. But it is a very useful **practical tolerance relation**.

So in the paper, call it:

[
\textbf{(\tau)-semantic equivalence}
]

or more carefully:

[
\textbf{(\tau)-behavioral equivalence under model (M)}.
]

The best definition:

[
(x,C)\sim_{\tau,M,k}(k(x),k(C))
]

iff

[
d\left(
f_M(x\mid C),
f_M(k(x)\mid k(C))
\right)
\le \tau.
]

This makes clear that equivalence is:

* model-relative,
* distance-relative,
* compressor-relative,
* tolerance-relative.

---

## The rectangular residual

Your rule-of-thumb test is:

[
\Delta_{XC}
\lesssim
\Delta_X+\Delta_C.
]

Equivalently:

[
d(y_{00},y_{11})
\lesssim
d(y_{00},y_{10})+d(y_{00},y_{01}).
]

Define the residual:

[
R_k
===

\Delta_{XC}-\Delta_X-\Delta_C.
]

Or:

[
R_k
===

## d(y_{00},y_{11})

## d(y_{00},y_{10})

d(y_{00},y_{01}).
]

Then:

[
R_k \le 0
]

means compression effects are subadditive or stable.

[
R_k > 0
]

means joint compression introduces extra semantic drift.

For benchmarking, use:

[
R_k^+=\max(0,R_k).
]

Then a good compressor has:

[
\mathbb E[R_k^+] \approx 0
]

or

[
Q_{0.95}(R_k^+)\le \epsilon.
]

This gives you an empirical version of the rectangular inequality.

---

## What to measure experimentally

For each prompt/context pair ((x,C)), run caveman compression:

[
x'=k(x), \qquad C'=k(C).
]

Then measure:

### 1. Compression ratio

[
\rho_X=\frac{|k(x)|}{|x|}
]

[
\rho_C=\frac{|k(C)|}{|C|}.
]

This tells you how much token reduction caveman achieves.

### 2. Query perturbation

[
\Delta_X=d(y_{00},y_{10}).
]

This tells you how much the model output changes when only the user query is compressed.

### 3. Context perturbation

[
\Delta_C=d(y_{00},y_{01}).
]

This tells you how much the output changes when only the context is compressed.

### 4. Joint perturbation

[
\Delta_{XC}=d(y_{00},y_{11}).
]

This tells you how much the output changes when both are compressed.

### 5. Rectangular residual

[
R_k=\Delta_{XC}-\Delta_X-\Delta_C.
]

This detects hidden interaction effects.

### 6. Pass/fail under tolerance

Define:

[
\operatorname{pass}_\tau(y_i,y_j)=
\mathbf 1[d(y_i,y_j)\le \tau].
]

Then report:

[
P(\Delta_X\le \tau),
]

[
P(\Delta_C\le \tau),
]

[
P(\Delta_{XC}\le \tau).
]

This gives a very interpretable benchmark:

> In what percentage of cases did caveman compression preserve behavior within tolerance (\tau)?

---

## Why caveman is a great example

Caveman is interesting because it is neither random deletion nor ordinary summarization.

It tries to remove linguistic overhead:

```text
please could you maybe explain how I should implement this
```

becomes something like:

```text
explain implementation
```

This is exactly the type of compression that a strong LLM may already be internally robust to.

So caveman is a good probe for the hypothesis:

[
\text{Many natural-language tokens are low-impact under }M.
]

In other words:

> Caveman compression tests whether the model already ignores, downweights, or marginalizes certain words.

This connects directly to attention and functional invariance.

If the model is good, then:

[
f_M(x\mid C)
\approx
f_M(k(x)\mid C)
]

because the removed tokens were not functionally important.

But caveman is also dangerous enough to be scientifically useful, because it can break coherence.

---

## Why semantic coherence may break

Caveman compression may remove words that look low-information locally but are globally important.

Examples:

### 1. Negation

Original:

```text
Do not delete the existing records.
```

Caveman-compressed:

```text
delete existing records
```

Here one small word flips the meaning.

Distance should rise sharply:

[
d(y_{00},y_{10}) \gg 0.
]

### 2. Modality

Original:

```text
Could this be unsafe under some conditions?
```

Compressed:

```text
unsafe conditions
```

The question type changes.

### 3. Politeness that encodes uncertainty

Original:

```text
I am not sure, but maybe this assumption is wrong.
```

Compressed:

```text
assumption wrong
```

The epistemic status changes from uncertain to assertive.

### 4. Scope

Original:

```text
Only compress the user query, not the system instruction.
```

Compressed:

```text
compress user query system instruction
```

The constraint boundary breaks.

### 5. Causal relations

Original:

```text
If A fails, then B should not be executed.
```

Compressed:

```text
A fails B executed
```

The conditional structure may be destroyed.

### 6. Context coupling

The query alone may survive compression:

[
d(y_{00},y_{10})\le \tau.
]

The context alone may survive compression:

[
d(y_{00},y_{01})\le \tau.
]

But together they may fail:

[
d(y_{00},y_{11})>\tau.
]

That is exactly what the rectangular residual detects.

---

## Why entropy may rise

This is a very important point.

Caveman compression reduces token count, but it can increase **semantic uncertainty**.

Original text may contain redundancy that disambiguates intent. When caveman removes that redundancy, the prompt becomes shorter but more ambiguous.

So token entropy may go down, but output entropy may go up.

In distributional terms, the original prompt induces:

[
P_M(\cdot\mid x,C).
]

The compressed prompt induces:

[
P_M(\cdot\mid k(x),C).
]

If compression removes disambiguating information, then:

[
H(P_M(\cdot\mid k(x),C))

>

H(P_M(\cdot\mid x,C)).
]

That means the model becomes less certain about what answer to produce.

So caveman can create this paradox:

[
|k(x)| < |x|
]

but

[
H(Y\mid k(x),C) > H(Y\mid x,C).
]

In words:

> The input is shorter, but the model’s output distribution becomes broader.

That is where semantic coherence breaks.

This is one of the strongest experimental angles.

---

## Entropy experiment

For models where token probabilities are available, measure:

[
H_M(Y\mid x,C)
]

and

[
H_M(Y\mid k(x),C).
]

Then define entropy rise:

[
E_k(x,C)
========

## H_M(Y\mid k(x),C)

H_M(Y\mid x,C).
]

If:

[
E_k>0,
]

then caveman compression made the model less certain.

You can also approximate this with repeated sampling:

Generate (n) outputs from each condition.

If compressed prompts produce more diverse answers, then entropy has likely increased.

Approximate by measuring pairwise diversity:

[
\operatorname{Div}(Y_k)
=======================

\mathbb E_{i,j}
[
d(y_k^{(i)},y_k^{(j)})
].
]

Then compare:

[
\operatorname{Div}(Y_{k(x)})-\operatorname{Div}(Y_x).
]

If this is positive, caveman compression increases output uncertainty.

---

## Full benchmark score

A practical caveman score could be:

[
S(k)
====

\lambda_1 \mathbb E[\rho_X]
+
\lambda_2 \mathbb E[\rho_C]
+
\lambda_3 \mathbb E[\Delta_X]
+
\lambda_4 \mathbb E[\Delta_C]
+
\lambda_5 \mathbb E[R_k^+]
+
\lambda_6 \mathbb E[\max(0,E_k)].
]

Where:

[
\rho_X,\rho_C
]

measure compression ratio.

[
\Delta_X,\Delta_C
]

measure response perturbation.

[
R_k^+
]

measures joint compression instability.

[
E_k
]

measures entropy rise.

Lower score means better compression.

---

## What the paper can claim experimentally

The paper can test hypotheses like:

### H1

Caveman achieves strong token reduction with low average response perturbation on technical prompts.

[
\rho_k \ll 1,\qquad \mathbb E[\Delta_X]\le \tau.
]

### H2

Caveman fails on prompts where small function words carry semantic load.

Examples: negation, quantifiers, conditionals, temporal constraints, legal instructions.

### H3

Entropy rise predicts failure.

If:

[
H(Y\mid k(x),C)-H(Y\mid x,C)>0,
]

then the compressed prompt is more likely to fail (\tau)-equivalence.

### H4

The rectangular residual detects failures that simple pairwise compression tests miss.

Even when:

[
\Delta_X\le\tau
]

and

[
\Delta_C\le\tau,
]

one may still have:

[
\Delta_{XC}>\tau.
]

This means query and context were individually compressible but not jointly compressible.

---

## Final compact framing

Caveman is a great benchmark object because it sits exactly at the boundary between:

[
\text{useful redundancy removal}
]

and

[
\text{semantic coherence collapse}.
]

When it works, it reveals model-relative invariance:

[
f_M(x\mid C)
\approx
f_M(k(x)\mid k(C)).
]

When it fails, it reveals that the removed words were not redundant after all.

The benchmark should therefore measure four things:

[
\boxed{
\text{compression ratio}
}
]

[
\boxed{
\tau\text{-behavioral equivalence}
}
]

[
\boxed{
\text{rectangular residual}
}
]

[
\boxed{
\text{entropy rise}
}
]

That gives you a strong experimental story:

> Caveman compression is not merely a way to save tokens. It is a probe of which parts of natural language are functionally active for a given LLM, and where semantic coherence breaks when low-information-looking tokens are removed.
