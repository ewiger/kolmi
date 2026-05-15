> Understanding the relationship between text entropy, semantic coherence, and model compression.

- [ ] NCD as approximation to NID but using LLM-based compressors (see kcp.py or think nncp by F. Bellard).
- [ ] Make a conclusion or observation (still a hypothesis) that low entropy of text per model M indicates high semantical coherence of text in a certain range.. when the entropy is to low the text is highly compressed and repetitive, and thus tautological. However, when tokens are meaningfully predicted by the model then there is a "golden middle" for text to be semantically rich and compressed. however as text becomes highly random and incompressible, then it is also semantically incoherent. Thus, there is a "sweet spot" for text to be semantically rich and compressed, which can be measured by the entropy of the text per model M.
- [ ] Formalize entropy sweet spot: define lower bound (tautology threshold) and upper bound (incoherence threshold) in terms of entropy percentiles or model-specific calibration.
- [ ] Connect entropy sweet spot to idempotence: text in sweet spot should exhibit stable semantic projections.
- [ ] Validate sweet spot hypothesis on diverse text corpora (Wikipedia, arXiv, legal, code).
