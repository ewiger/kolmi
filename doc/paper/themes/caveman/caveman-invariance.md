---
Yes — I agree with your correction.

If (C') says “be short,” then this is not a clean context perturbation. It is too strong because it changes the **output policy**, not merely the semantic/background context. So in your framework, that should be considered an invalid or contaminated (C') for the rectangular test.

A cleaner assumption is:

[
C' = k_C(C)
]

where (k_C) is a caveman-style compression of context, not a new instruction like “be brief.”

So instead of:

[
C' = \text{“answer shortly”},
]

you want:

[
C' = k(C),
]

where (C') preserves the same role, task, facts, constraints, and intent, but removes low-information tokens.

Then the four points become:

[
y_1=f_M(x\mid C)
]

[
y_2=f_M(k(x)\mid C)
]

[
y_3=f_M(x\mid k(C))
]

[
y_4=f_M(k(x)\mid k(C)).
]

That is much stronger and much cleaner.

Now the rectangle tests:

> What happens when we compress the user query, the context, or both?

Not:

> What happens when we ask the model to change style?

So the real square is:

[
(x,C)
\to
(k(x),C)
]

[
(x,C)
\to
(x,k(C))
]

[
(x,C)
\to
(k(x),k(C)).
]

Then:

[
d_k(y_1,y_2)
]

means semantic response change from **query compression**.

[
d_k(y_1,y_3)
]

means semantic response change from **context compression**.

[
d_k(y_1,y_4)
]

means semantic response change from **joint query/context compression**.

The residual:

[
R_k
===

## d_k(y_1,y_4)

## d_k(y_1,y_2)

d_k(y_1,y_3)
]

then measures whether compressing both creates unexpected interaction damage.

That is exactly the right object.

---

Your deeper intuition about attention and model compression is also interesting:

> If a good LLM already learns to downweight low-information words through attention, then caveman compression may approximate what the model internally ignores.

So (k) is not arbitrary text shortening. It is a hypothesis about the model’s internal invariances.

Roughly:

[
f_M(x\mid C)
\approx
f_M(k(x)\mid k(C))
]

when (k) removes tokens that contribute little to the model’s final computation.

This connects semantic compression to something like **functional model invariance**.

You can phrase it like this:

[
k \text{ is good for } M
\iff
M \text{ is approximately invariant under } k.
]

Formally:

[
\Delta_k^M(x,C)
===============

d\left(
f_M(x\mid C),
f_M(k(x)\mid k(C))
\right)
]

should be small.

This means the compressor (k) exposes a symmetry or near-symmetry of the model:

[
(x,C)
\sim_M
(k(x),k(C)).
]

That is better than saying “the meaning is preserved” in an absolute human sense. It says:

> The model’s input-output behavior is approximately invariant under this compression map.

---

The connection to weight/model compression can be stated as an analogy:

### Weight compression

A model compressor removes parameters or precision while preserving function:

[
M \to M'
]

such that

[
f_M(x)\approx f_{M'}(x).
]

### Prompt/context compression

A prompt compressor removes input tokens while preserving function:

[
(x,C)\to(k(x),k(C))
]

such that

[
f_M(x\mid C)\approx f_M(k(x)\mid k(C)).
]

So both are forms of **functional compression**.

One compresses the model:

[
M \mapsto M'
]

The other compresses the input:

[
(x,C)\mapsto(k(x),k(C)).
]

Both are judged by behavioral preservation.

You could put this in the paper as a central analogy:

[
\boxed{
\text{Prompt compression is input-side functional compression.}
}
]

And:

[
\boxed{
\text{Model compression is parameter-side functional compression.}
}
]

This is a very nice conceptual bridge.

---

The DeepSeek-style connection is approximately:

> Modern efficient models suggest that large parts of computation can be sparsified, routed, distilled, quantized, or otherwise compressed without proportionally losing capability. Caveman compression asks a parallel question on the input side: how many prompt tokens are functionally inactive or low-impact for the model’s computation?

So the paper can speculate:

[
\text{attention sparsity}
\Rightarrow
\text{input-token redundancy}
\Rightarrow
\text{semantic compressibility}.
]

But keep it as a hypothesis, not a theorem.

A good hypothesis name:

[
\textbf{Attention-Redundancy Hypothesis}
]

Possible statement:

> For sufficiently capable language models, many natural-language prompt tokens have low marginal influence on the output distribution. A semantic compressor (k) attempts to remove or rewrite these tokens while preserving the model’s functional behavior.

More formally, with output distributions:

[
P_M(\cdot\mid x,C)
\approx
P_M(\cdot\mid k(x),k(C)).
]

Or using a distance:

[
D\left(
P_M(\cdot\mid x,C),
P_M(\cdot\mid k(x),k(C))
\right)
\le \tau.
]

This is even cleaner than string-output comparison.

---

Then your rectangular inequality becomes a diagnostic for **compositional invariance**:

[
d(y_1,y_4)
\lesssim
d(y_1,y_2)+d(y_1,y_3).
]

where now:

[
y_1=f_M(x\mid C)
]

[
y_2=f_M(k(x)\mid C)
]

[
y_3=f_M(x\mid k(C))
]

[
y_4=f_M(k(x)\mid k(C)).
]

Interpretation:

> If query compression and context compression each individually preserve model behavior, then jointly compressing both should not create much extra drift.

The residual:

[
R_k
===

d(y_1,y_4)-d(y_1,y_2)-d(y_1,y_3)
]

measures failure of compositionality.

High positive (R_k) means:

> The query and context looked compressible separately, but not together.

That is very important for agent memory, RAG, and system-prompt compression.

---

I would revise the paper’s core framework to this:

Let

[
k_X
]

compress user queries, and

[
k_C
]

compress context.

Often they may be the same algorithm:

[
k_X=k_C=k.
]

Define:

[
y_{00}=f_M(x\mid C)
]

[
y_{10}=f_M(k_X(x)\mid C)
]

[
y_{01}=f_M(x\mid k_C(C))
]

[
y_{11}=f_M(k_X(x)\mid k_C(C)).
]

Then:

[
\Delta_X=d(y_{00},y_{10})
]

[
\Delta_C=d(y_{00},y_{01})
]

[
\Delta_{XC}=d(y_{00},y_{11})
]

[
R_{XC}=\Delta_{XC}-\Delta_X-\Delta_C.
]

This notation is clearer than (y_1,\ldots,y_4).

The empirical rule:

[
\boxed{
R_{XC}^{+}
==========

\max(0,R_{XC})
\text{ should be small.}
}
]

And the benchmark score:

[
S(k)
====

\lambda_1 \rho_X
+
\lambda_2 \rho_C
+
\lambda_3 \mathbb E[\Delta_X]
+
\lambda_4 \mathbb E[\Delta_C]
+
\lambda_5 \mathbb E[R_{XC}^{+}].
]

where:

[
\rho_X=\frac{|k_X(x)|}{|x|}
]

[
\rho_C=\frac{|k_C(C)|}{|C|}.
]

---

The important philosophical shift is:

You are not saying:

> (k) preserves semantics because humans agree it does.

You are saying:

> (k) exposes input redundancies under a fixed model (M), similar to how pruning/quantization/distillation expose parameter redundancies in model compression.

That is a strong paper idea.

Final crisp formulation:

[
\boxed{
\text{Caveman compression is a probe of model-relative semantic invariance.}
}
]

Or:

[
\boxed{
\text{A prompt is semantically compressible for }M
\text{ if }M\text{'s behavior is stable under }x\mapsto k(x).
}
]

And the context version:

[
\boxed{
\text{A prompt-context pair }(x,C)\text{ is jointly compressible if }
f_M(x\mid C)
\approx
f_M(k(x)\mid k(C)).
}
]

That is the cleanest direction for the paper.


---
