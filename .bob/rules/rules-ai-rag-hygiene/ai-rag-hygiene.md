# RAG & Embedding Hygiene
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: AI Engineer -->

- Pin the embedding model and its dimension; re-embed the whole corpus on any change
  — never mix vectors from different models/dimensions in one index.
- Every chunk carries provenance (source id, title, location); responses cite sources.
- Chunk deliberately (bounded size + overlap); don't embed whole documents blindly.
- No secrets or real PII in the vector store; synthetic content only for demos.
- Ground answers in retrieved context; if retrieval is empty/low-score, say so —
  do not let the model free-form an unsupported answer.
