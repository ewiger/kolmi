
# Theoretical framework

## Part 1: Theoretical framework for understanding the relationship between text entropy, semantic coherence, and model compression.

- [ ] NCD as approximation to NID but using LLM-based compressors (see kcp.py or think nncp by F. Bellard).
- [ ] Make a conclusion or observation (still a hypothesis) that low entropy of text per model M indicates high semantical coherence of text in a certain range.. when the entropy is to low the text is highly compressed and repetitive, and thus tautological. However, when tokens are meaningfully predicted by the model then there is a "golden middle" for text to be semantically rich and compressed. however as text becomes highly random and uncompressible, then it is also semantically incoherent. Thus, there is a "sweet spot" for text to be semantically rich and compressed, which can be measured by the entropy of the text per model M.
- [ ] Formalize entropy sweet spot: define lower bound (tautology threshold) and upper bound (incoherence threshold) in terms of entropy percentiles or model-specific calibration.
- [ ] Connect entropy sweet spot to idempotence: text in sweet spot should exhibit stable semantic projections.
- [ ] Validate sweet spot hypothesis on diverse text corpora (Wikipedia, arXiv, legal, code).

## Part 2: What are "directions" of semantical compression? Defining the notion of "utility" or "sense" for semantical compression.

> all the previous points are still do not talk about such notion as "utility" or "sense" as it can be used in what we define as "semantical compression". We can say that the "sense" of a text is related to its "utility" for a certain task or purpose.

- [ ] Define an abstract infinite index set that enumerates all possible "utilities" or "senses" for the sematic compression. As such sematic compression is actually alway a form of the LLM task for summarization, but the "utility" or "sense" of the summarization can be different for different tasks or purposes. For example, a summarization that is useful for a legal document may not be useful for a scientific paper, and vice versa. 
- [ ] Formalize utility space U as a topological or measure-theoretic object (not just a discrete enum).
- [ ] Define utility-conditioned idempotence: f_u(f_u(x)) ≈ f_u(x) for each u ∈ U separately.
- [ ] Show how different utilities induce different quotient partitions: X/~_u vs X/~_u'.
- [ ] Establish partial order over utilities via refinement: f_a ⪯ f_b iff utilities are comparable.

## Part 3: Caveman's 2×2 Grid and τ-Tolerance Equivalence

Caveman compression is evaluated via a rectangular (2×2) functional behavior test. This is the core methodological innovation.

- [ ] Define the 2×2 grid of compressed and uncompressed query/context:
  - y_{00} = f_M(x | C): baseline output
  - y_{10} = f_M(k(x) | C): query compressed, context intact
  - y_{01} = f_M(x | k(C)): query intact, context compressed
  - y_{11} = f_M(k(x) | k(C)): both query and context compressed.
- [ ] Interpret each: y_{10} tests query-compression robustness; y_{01} tests context-compression robustness; y_{11} tests joint compression robustness.
- [ ] Define utility-specific distance d_k that measures semantic drift in model outputs (e.g., token-level or probabilistic distance).
- [ ] Define τ-tolerance equivalence: (x,C) ~_{τ,M,k} (k(x),k(C)) iff d_k(y_{00}, y_{11}) ≤ τ.
  - This is model-relative (depends on M), distance-relative (depends on d_k), compressor-relative (depends on k), and tolerance-relative (depends on τ).
  - Emphasize this is a practical tolerance relation, not a strict mathematical equivalence (transitivity may fail).
- [ ] Define perturbation measures:
  - Δ_X = d_k(y_{00}, y_{10}): semantic change from query compression
  - Δ_C = d_k(y_{00}, y_{01}): semantic change from context compression
  - Δ_{XC} = d_k(y_{00}, y_{11}): semantic change from joint compression.
- [ ] Define interaction residual: R_k = Δ_{XC} - Δ_X - Δ_C.
  - R_k ≤ 0: compression effects are subadditive (stable or better than expected).
  - R_k > 0: joint compression introduces extra semantic drift (non-linear interaction).
- [ ] Establish rule-of-thumb: E[R_k^+] ≈ 0 or Q_{0.95}(R_k^+) ≤ ε, where R_k^+ = max(0, R_k).

## Part 4: Quality Metrics for Caveman Compression

Define comprehensive quality criteria balancing compression efficiency, semantic fidelity, and compositional stability.

- [ ] Define compression ratios:
  - ρ_X = |k(x)| / |x|: query token reduction ratio
  - ρ_C = |k(C)| / |C|: context token reduction ratio.
- [ ] Define semantic distortions (using model output distance d_k):
  - Δ_X = d_k(y_{00}, y_{10}): query-compression semantic perturbation
  - Δ_C = d_k(y_{00}, y_{01}): context-compression semantic perturbation
  - Δ_{XC} = d_k(y_{00}, y_{11}): joint compression semantic perturbation.
- [ ] Define interaction residual: R_k = Δ_{XC} - Δ_X - Δ_C.
  - Diagnostic: positive residuals indicate non-linear interaction damage.
  - Use R_k^+ = max(0, R_k) for penalty enforcement.
- [ ] Propose multi-objective quality score for caveman:
  S(k) = λ_1 E[ρ_X] + λ_2 E[ρ_C] + λ_3 E[Δ_X] + λ_4 E[Δ_C] + λ_5 E[R_k^+].
  - Lower is better. Typical weights: λ_1, λ_2 ∈ [0.1, 0.3] (compression priority), λ_3, λ_4 ∈ [0.2, 0.5] (semantic fidelity), λ_5 ∈ [0.1, 0.4] (stability penalty).
- [ ] Define pass/fail thresholds: report P(Δ_X ≤ τ), P(Δ_C ≤ τ), P(Δ_{XC} ≤ τ) for practical tolerance τ.
  - This gives percentage of test cases where caveman compression preserves behavior within tolerance.
- [ ] Formalize caveman quality as a diagnostic: S(k) is good iff high compression (low ρ_X, ρ_C) AND low distortion (low Δ_X, Δ_C) AND low residual (low R_k^+).




# Experimental Design

## Part 5: Experimental Design and Validation

- [ ] Choose 2–3 LLM models (e.g., GPT-3.5, GPT-4, Llama 2 or similar).
- [ ] Define utility set: summarization, legal-extraction, causal-extraction, code-preservation, safety-extraction, emotional-tone-preservation.
- [ ] For each utility, specify compressor instruction and ground truth or proxy labels.
- [ ] Create test corpus covering: web text, academic text, code, legal documents, social media.
- [ ] Design idempotence experiment: apply f_u repeatedly and track d_u(x, f_u(x)) decay.
- [ ] Design comparability experiment: test if f_a ∘ f_b ≈ f_a for each utility pair.
- [ ] Design quality experiment: measure ρ, Δ, Γ, R across utilities and models.
- [ ] Create Pareto-front visualization: compression ratio vs distortion vs residual.
- [ ] Validate that utilities cluster into comparable/incomparable groups.

## Part 6: Implementation and Tooling

- [ ] Integrate kcp.py for LLM-based compression (NCD approximation).
- [ ] Build entropy computation module: H_M(x) per model M.
- [ ] Implement utility-conditioned prompting framework (f_u via instruction).
- [ ] Create distortion/residual logging and aggregation pipeline.
- [ ] Build plotting utilities for entropy histograms, idempotence curves, comparability matrices, Pareto fronts.
- [ ] Design reproducibility: save seeds, model checkpoints, prompt templates, and raw metrics.

## Part 7: Narrative and Presentation

- [ ] Ensure introduction motivates both layers: universal coherence AND utility indexing.
- [ ] Use unified notation: X, U, C(x, u), f_u, H_M(x), NCD, NID, d_u.
- [ ] Include worked examples:
  - (a) Same text, different models → different entropy sweet spots.
  - (b) Same text, different utilities → incomparable quotients.
  - (c) Compression-utility interaction: why some (k, u) pairs have high residuals.
- [ ] Highlight balance: universal coherence as foundation, utility-indexing as refinement.
- [ ] Address counterexamples: when entropy sweet spot fails or utilities defy order.
- [ ] Future work: learned utility spaces, adaptive optimization, alignment via entropy calibration.

## Part 8: Bibliography and Related Work

- [ ] Add papers on information-theoretic coherence (e.g., coherence models in NLP).
- [ ] Add papers on NCD/NID applications (Li, Vitányi et al.).
- [ ] Add papers on semantic compression (summarization, question answering).
- [ ] Add papers on idempotent and fixed-point semantics (neural networks, symbolic systems).
- [ ] Add papers on model ranking via compression.
- [ ] Add papers on semantic similarity and paraphrase robustness.
- [ ] Organize by theme in references.bib and cite consistently.

## Part 9: Specific Sections to Draft

- [ ] Section 2 (Entropy & Sweet Spot): hypothesis, formalization, intuition, limitations.
- [ ] Section 3 (NID/NCD): review Kolmogorov complexity, define NID, justify NCD as proxy.
- [ ] Section 4 (Problem Setup): define X, U, C(x, u), f_u, equivalence.
- [ ] Section 5 (Idempotence): present f_u ∘ f_u ≈ f_u, discuss fixed points and attractors.
- [ ] Section 6 (Quotients & Order): define X/~_u, refinement relation, composition law.
- [ ] Section 7 (Utility-Aware Distance): d_u formalism, metric properties, feature selection view.
- [ ] Section 8 (Quality): distortion decomposition, objective S(k), empirical criteria.

## Part 10: Validation Checklist

- [ ] Run entropy analysis on 10k+ diverse texts; confirm sweet-spot clustering.
- [ ] Test idempotence: f_u^(20)(x) vs f_u^(1)(x) convergence per utility.
- [ ] Test comparability: measure f_a ∘ f_b vs f_a on held-out test set.
- [ ] Test quality: does S(k) correlate with human semantic preservation judgments?
- [ ] Test across models: do results generalize to multiple LLM families?
- [ ] Sensitivity analysis: how do λ weights in S(k) affect utility rankings?
- [ ] Failure mode analysis: when does entropy sweet spot hypothesis break?
- [ ] Ablation: remove utility indexing and show single-chain view is incomplete.

