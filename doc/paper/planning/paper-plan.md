# Paper Structure and Plan

## Goal
Build a theory-and-evidence paper around semantic compression as a dual-layer framework: universal semantic coherence (entropy sweet spot) parameterized by utility-conditioned compression directions.

## Core Thesis
Semantic compression has two levels: (1) a universal layer where text has an entropy sweet spot indicating semantic coherence and non-tautological meaningful predictability, and (2) a utility-indexed layer where different compression directions preserve different semantic properties. The family of instruction-conditioned semantic projectors and quotients forms a typed partial order over compatible utilities.

## Proposed Paper Structure

### Layer 1: Universal Semantic Coherence
1. Introduction
   - Motivate semantic compression beyond token reduction.
   - State the dual-layer claim: universal coherence + utility-indexed directions.

2. Text Entropy and Semantic Coherence Hypothesis
   - Define entropy H_M(x) of text x under model M.
   - Propose sweet spot hypothesis: semantic coherence ≠ low entropy alone.
   - When entropy is too low: text is tautological and repetitive.
   - When entropy is too high: text is uncompressible and incoherent.
   - Claim: optimal range exists where text is semantically rich yet meaningfully compressible.
   - Operationalize with entropy percentiles or model-specific thresholds.

3. NID and NCD as Universal Measures
   - Define ideal NID (Kolmogorov) and practical NCD (LLM-based).
   - Frame NCD as LLM compression approximation to algorithmic distance.
   - Show how NCD/NID can serve as universal semantic coherence metrics.

### Layer 2: Utility-Indexed Compression Directions
4. Problem Setup and Notation
   - Define language space X and utility space U as abstract infinite index set.
   - Define compressor family C(x, u) = f_u(x) where u ∈ U indexes compression direction.
   - Clarify that utilities define what semantic information must be preserved.
   - Differentiate exact vs approximate semantic equivalence.

5. Instruction-Conditioned Idempotent Projectors
   - Present approximate idempotence f_u(f_u(x)) ≈ f_u(x) for fixed u.
   - Interpret as semantic stabilization under fixed utility regime.
   - Discuss fixed points and attractor intuition per utility.

6. Utility-Relative Quotients and Refinement Order
   - Define utility-relative quotient X/~_u and equivalence x ∼_u y.
   - Define order relation f_a ⪯ f_b via equivalence refinement.
   - Composition criterion: f_a ∘ f_b ≈ f_a for coarser f_a.
   - Distinguish comparable vs incomparable utility pairs.
   - Show why utilities form a partially ordered family, not a single chain.

7. Distance Layer: Utility-Aware NID and NCD
   - Define utility-aware distance d_u(x, y) on compressed representations.
   - Show how utility choice determines what semantic similarity is visible.
   - Connect universal coherence metrics to utility-specific distance.

8. Quality of Semantic Compression
   - Define distortion decomposition for model outputs under compression and context changes:
     - Δ: compression perturbation
     - Γ: context perturbation
     - J: joint perturbation
     - R: interaction residual
   - Define objective S(k) balancing compression ratio, distortion, and residual.
   - Frame as heuristic regularity criterion, not strict axiom.

9. Experimental Program
   - Universal layer experiments:
     - Entropy distributions and sweet-spot identification per model.
     - Correlation between entropy and semantic coherence scores.
   - Utility layer experiments:
     - Utilities: summarization, legal extraction, causal extraction, code-preservation, safety-relevance.
     - Models: 2–3 LLM families.
     - Evaluation outputs: idempotence curves, utility comparability matrix, Pareto fronts (ratio vs distortion vs residual).

10. Results and Discussion
    - Which utilities form chains vs incomparable clusters.
    - Whether low token ratio predicts semantic quality per utility.
    - Entropy sweet spot evidence and failure modes.
    - Failure cases where residuals are large.

11. Related Work and Positioning
    - Compression-based ranking and calibration.
    - Information-theoretic measures of semantic coherence.
    - Paraphrase robustness and self-consistency.
    - Idempotent and invariance-style neural formulations.

12. Conclusion and Future Work
    - Summarize dual-layer view: universal + utility-indexed.
    - Future directions: learned utility spaces, adaptive utility selection, entropy-sweet-spot optimization for model alignment.

