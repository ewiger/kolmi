Your formula is actually reasonable — but it is **not Shannon entropy itself**. It is an **empirical cross-entropy rate estimate** measured in bits per token.

The confusion comes from mixing:

* Shannon entropy,
* cross-entropy,
* code length,
* Kolmogorov complexity.

They are related but not identical.

---

# 1. Shannon entropy

For a random variable (X) with probabilities (p(x)):

H(X)=-\sum_x p(x)\log_2 p(x)

The logarithm appears because information content is:

[
I(x)=-\log_2 p(x)
]

measured in bits.

---

# 2. Language-model entropy coding

Your compressor uses token probabilities predicted by the LLM:

[
p_M(t_i \mid t_{<i})
]

Arithmetic coding then achieves approximately:

[
|z_M(x)| \approx -\sum_i \log_2 p_M(t_i \mid t_{<i})
]

THIS is where the logarithm lives.

So the code length already internally contains the log term.

That means your:

h_M(x)=\frac{|z_M(x)|}{|x|_{\mathrm{tok}}}

is approximately:

[
h_M(x)
\approx
\frac{1}{n}
\sum_{i=1}^n
-\log_2 p_M(t_i\mid t_{<i})
]

which is standard average negative log-likelihood per token.

---

# 3. What this quantity really is

More precisely:

* if (M) equals the true distribution:

  * this converges to Shannon entropy rate;

* otherwise:

  * this is cross-entropy rate.

So mathematically the cleaner wording is:

[
h_M(x)
]

is a **model-relative empirical cross-entropy estimate**.

NOT strictly “entropy.”

---

# 4. Relation to Kolmogorov complexity

Kolmogorov complexity:

[
K(x)
]

is shortest program length generating (x).

Shannon entropy is statistical expectation over distributions.

The bridge is:

For stationary ergodic sources:

[
K(x_{1:n}) \approx n H
]

asymptotically.

And practical compressors approximate this through code length.

So your:

[
|z_M(x)|
]

acts as:

* practical entropy code length,
* approximation to compressibility,
* heuristic proxy for Kolmogorov complexity.

But only asymptotically and model-relatively.

---

# 5. Suggested correction in paper

Instead of:

> “per-token model entropy estimate”

write:

> “per-token model-relative cross-entropy estimate”

or:

> “empirical code-length rate”

This is much more precise mathematically.

For example:

[
h_M(x):=\frac{|z_M(x)|}{|x|_{\mathrm{tok}}}
]

denotes the average number of bits per token produced by arithmetic coding under model (M), approximating the empirical cross-entropy rate of (x) under (M).

That wording is solid.
