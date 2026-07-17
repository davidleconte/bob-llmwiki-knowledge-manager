# Plan: MiniLM / mlx-embeddings Documentation Updates

**Branch:** `fix-multilevel-cache-race`
**Scope:** Document the optional MiniLM backend added in step 3 of the KB embedding pipeline improvements. No code changes.

---

## Overview

The `EmbeddingGenerator` class gained an optional `backend="minilm"` parameter that loads `sentence-transformers/all-MiniLM-L6-v2` via `mlx-embeddings` on Apple Silicon. This feature ships with zero documentation outside the module docstring. Three user-facing documentation gaps must be closed:

1. Users don't know the feature exists or how to activate it.
2. Users may assume a HuggingFace API key is required (it is not — the model is public).
3. The architecture document does not reflect the new embedding subsystem.
4. The security/threat model is now out of date (new outbound network path: model download).

**Key facts confirmed from code:**
- Model: `sentence-transformers/all-MiniLM-L6-v2` (public HuggingFace Hub, no auth required)
- Install: `pip install -e ".[mlx]"` — optional extra, macOS + Apple Silicon only
- Fallback: silent `UserWarning` + automatic fall back to `HashingVectorizer` if `mlx-embeddings` absent
- Download: first use triggers one-time ~22MB download to `~/.cache/huggingface/` (standard HF Hub cache)
- No HuggingFace API key needed for public models
- Performance: ~2–4 ms/call warm (Apple Neural Engine), vs <1 ms HashingVectorizer
- Dim: 384 (MiniLM) vs 1000 (HashingVectorizer) — mismatch triggers automatic index rebuild
- `backend` arg is not wired to any config file or env var — code-only for now

**Non-goals:**
- No code changes of any kind.
- No new ADR (the design choice is already in ADR-014 context; the MiniLM addition is an implementation detail, not a new architectural decision).
- No changes to `docs/INSTALLATION.md` (that document is scoped to the Bash KB Manager only; Python TOS install is already covered in §8 of README.md).
- No creation of a new `docs/INSTALLATION_PYTHON_SYSTEM.md` — the scope is *documenting the MiniLM feature*, not writing a full Python system install guide (that is a separate, larger effort).

---

## Sub-Tasks

---

### Sub-task 1 — Update `README.md §8` and `§12`

**Status:** `[ ] pending`

**Intent:**
`README.md §8` ("Using the Token Optimization System") currently says `pip install -e ".[dev,monitoring]"` and nothing else about extras or the embedding backend. A new user reading that section will not know the MiniLM backend exists or how to enable it. `§12` (Security) states "no outbound traffic (except optional tiktoken BPE vocab download)" — this is now inaccurate since `mlx-embeddings` triggers a model download on first use.

**Expected Outcomes:**
- `README.md §8` has a new subsection "Optional: MiniLM semantic embedding backend" with platform support table, install command, and explicit "no API key required" note.
- `README.md §12` (Security) paragraph is updated to name both the tiktoken download and the `mlx-embeddings` model download as the two outbound paths, with the note that the model download only occurs when `backend="minilm"` is used.
- No other sections of README.md are touched.

**Todo List:**
1. In `README.md §8`, after the existing `pip install -e ".[dev,monitoring]"` line, add a new subsection `### Optional: MiniLM semantic embedding backend` containing:
   - One-sentence explanation of what MiniLM gives (384-dim semantic vectors, Apple Neural Engine, ~2–4 ms)
   - Install command: `pip install -e ".[mlx]"`
   - Platform support table: macOS + Apple Silicon (✅ Full), macOS + Intel (⚠️ falls back to HashingVectorizer silently), Linux (⚠️ falls back silently)
   - Explicit callout: "**No HuggingFace API key required.** `sentence-transformers/all-MiniLM-L6-v2` is a public model. On first use, `mlx-embeddings` downloads it once (~22 MB) to `~/.cache/huggingface/`."
   - Fallback guarantee: "If `mlx-embeddings` is absent, `EmbeddingGenerator` emits a warning and silently uses HashingVectorizer — KB retrieval is never blocked."
2. In `README.md §12`, update the sentence "no outbound traffic (except optional tiktoken BPE vocab download)" to read: "no outbound traffic except two optional first-use downloads: tiktoken BPE vocabulary (`src/optimizer/token_counter.py:38-46`) and, when `backend="minilm"` is used, the `sentence-transformers/all-MiniLM-L6-v2` model via `mlx-embeddings` (~22 MB, cached to `~/.cache/huggingface/`, not triggered on CI or default configuration)."

**Relevant Context:**
- `README.md:247` — existing `pip install` line in §8
- `README.md:426` — existing §12 Security paragraph
- `src/cache/embeddings.py:40-53` — `_try_load_minilm()` fallback logic (the source of the "emits a warning" claim)
- `SECURITY.md:23-24` — the existing security scope statement (do NOT edit SECURITY.md in this sub-task — that is sub-task 4)

---

### Sub-task 2 — Update `docs/architecture/ARCHITECTURE.md §5`

**Status:** `[ ] pending`

**Intent:**
The §5 "Components" section describes `src/cache/` as using "TF-IDF similarity, ... deterministic (stateless `HashingVectorizer`)" — which is now accurate only for the default backend. The MiniLM backend is a documented, shipped alternative with different dimensionality, platform constraints, and performance characteristics. The architecture document must reflect this.

Additionally, the §2 component diagram shows no `src/embeddings/` subsystem at all. With `MarkdownChunker`, `PersistentEmbeddingIndex`, and `KBIndexer` now implemented, the architecture diagram note about "deliberately separate" modules needs updating.

**Expected Outcomes:**
- `§5 Components` accurately describes `EmbeddingGenerator` with both backends: HashingVectorizer (default, 1000-dim, no deps) and MiniLM-L6-v2 (optional, 384-dim, Apple Silicon, `mlx-embeddings`).
- `§5` mentions the `src/embeddings/` subsystem (persistent index, chunker, indexer) as a deliberately-separate, opt-in layer for KB document search.
- `§2` note "Not shown, deliberately separate" is updated to include `src/embeddings/`.
- The phrase "TF-IDF similarity" is removed (HashingVectorizer is not TF-IDF; this is a pre-existing inaccuracy worth correcting here).
- No other sections of the architecture doc are modified.

**Todo List:**
1. In `§5 Components`, update the **Cache** bullet:
   - Replace "TF-IDF similarity" with "cosine similarity using `HashingVectorizer` (default) or `MiniLM-L6-v2` (optional)".
   - Add a note: `EmbeddingGenerator` supports two backends: `"hashing"` (1000-dim, stateless, no extra deps, works everywhere) and `"minilm"` (384-dim, Apple Silicon, requires `pip install -e "[mlx]"`; falls back silently when unavailable).
2. In `§5`, add a new bullet for `src/embeddings/` between the Cache and Optimizer bullets:
   - **KB Embedding Index (`src/embeddings/`).** Disk-backed embedding index for semantic KB document search. `MarkdownChunker` splits `.md` files on `##`-boundaries; `PersistentEmbeddingIndex` stores `[N×384]` or `[N×1000]` float32 vectors in `.bob/kb-index/`; `KBIndexer` drives incremental mtime/hash-based rebuild. Deliberately separate from the cache/optimizer pipeline — opt-in via `KnowledgeBaseQuery(index=...)` (ADR-015).
3. In `§2` "Not shown, deliberately separate" list, add `src/embeddings/` — the KB persistent embedding index and MarkdownChunker subsystem (opt-in, not on the `optimize()` request path).

**Relevant Context:**
- `docs/architecture/ARCHITECTURE.md:146-159` — existing §5 Components section
- `docs/architecture/ARCHITECTURE.md:66-77` — existing "Not shown" list in §2
- `src/cache/embeddings.py:73-80` — `EmbeddingGenerator.__init__` showing both backends
- `src/embeddings/index.py`, `src/embeddings/chunker.py`, `src/embeddings/indexer.py` — the subsystem being documented
- ADR-014 and ADR-015 for decision rationale (already written; just reference them)

---

### Sub-task 3 — Update `ADR-014` with MiniLM backend note

**Status:** `[ ] pending`

**Intent:**
ADR-014 was written before the MiniLM backend existed. It correctly documents the `HashingVectorizer`'s near-zero cosine similarity (0.091) and the A/B validation gate — but now the default backend for the KB embedding pipeline has changed. A reader of ADR-014 today will be confused: the A/B validation passed (`p@3=0.88`) but the document says "cosine similarity 0.091 means the HashingVectorizer is tuned for near-duplicate detection, not cross-vocabulary retrieval." The resolution of that tension (MiniLM) must be recorded in the ADR.

**Expected Outcomes:**
- ADR-014 has a new "## Amendment — MiniLM backend (2026-07)" section appended that:
  - Explains that step 3 of the KB embedding pipeline improvement added an optional `backend="minilm"` to `EmbeddingGenerator`.
  - Notes that with MiniLM the near-zero similarity problem is resolved (~0.78 cosine on semantically related pairs vs 0.091 with HashingVectorizer).
  - States clearly: "No HuggingFace API key is required; `sentence-transformers/all-MiniLM-L6-v2` is a public model."
  - States the fallback guarantee: when `mlx-embeddings` is absent, the generator falls back to `"hashing"` — the A/B validation gate still applies.
  - References `src/cache/embeddings.py` as the implementation.
- The original ADR body is not modified (ADRs are append-only).

**Todo List:**
1. Append a new `## Amendment — MiniLM backend (branch: fix-multilevel-cache-race)` section at the end of `docs/adr/014-kb-query-embedding-scorer.md` containing:
   - Date and context: "Following the A/B validation gate passing, step 3 of the KB embedding pipeline added an optional MiniLM-L6-v2 backend."
   - Cosine similarity improvement: HashingVectorizer ~0.091 → MiniLM ~0.78 on semantically related pairs.
   - Implementation: `EmbeddingGenerator(backend="minilm")` in `src/cache/embeddings.py`; model loaded lazily via `mlx-embeddings`.
   - HuggingFace requirement: "No API key required. The model `sentence-transformers/all-MiniLM-L6-v2` is public. First use triggers a one-time ~22 MB download to `~/.cache/huggingface/`."
   - Fallback: "When `mlx-embeddings` is absent (Linux, Intel Mac, CI), `EmbeddingGenerator` silently falls back to `"hashing"`. The A/B validation gate in this ADR continues to apply to both backends."
   - Platform: macOS + Apple Silicon only for the MiniLM path.

**Relevant Context:**
- `docs/adr/014-kb-query-embedding-scorer.md` — full file (read before editing)
- ADRs in this repo follow append-only convention — the existing body must not be modified
- `src/cache/embeddings.py:34-53` — `_try_load_minilm()` fallback (source for the fallback claim)

---

### Sub-task 4 — Update `SECURITY.md` and `docs/security/THREAT_MODEL.md`

**Status:** `[ ] pending`

**Intent:**
`SECURITY.md` currently states the system "makes no outbound network calls" except tiktoken. `THREAT_MODEL.md` §Deployment context says the same. Both are now inaccurate — `mlx-embeddings.load()` makes a network call to HuggingFace Hub on first use when `backend="minilm"`. This must be documented honestly, with the correct scope qualification: it only occurs when (a) `mlx-embeddings` is installed and (b) `EmbeddingGenerator(backend="minilm")` is called.

This is not a security vulnerability — it is a public model download, no different from tiktoken. But the threat model must be accurate. A fabricated "no network calls" claim after adding a network call would be a documentation integrity violation.

**Expected Outcomes:**
- `SECURITY.md` §"What this project is" paragraph accurately names both outbound paths (tiktoken + optional mlx model download) with the same conditional framing as the existing tiktoken mention.
- `THREAT_MODEL.md` §Deployment context bullet "makes no outbound network calls..." is updated to list both: tiktoken vocab (existing) and `mlx-embeddings` model download (new, conditional on `backend="minilm"`).
- Both documents remain accurate, honest, and consistent with the actual code behaviour.

**Todo List:**
1. In `SECURITY.md` (line ~24), update the parenthetical "(apart from tiktoken's optional first-use vocabulary download)" to read: "(apart from two optional first-use downloads: tiktoken BPE vocabulary, and the `sentence-transformers/all-MiniLM-L6-v2` model when `EmbeddingGenerator(backend="minilm")` is used — both downloads only occur on first use and only if the respective feature is activated; the default configuration makes neither call)".
2. In `docs/security/THREAT_MODEL.md` §Deployment context (line ~31), update the bullet "makes **no outbound network calls** from `src/` except tiktoken's optional first-use vocabulary download" to add: "and, optionally, the `sentence-transformers/all-MiniLM-L6-v2` model download via `mlx-embeddings` (`src/cache/embeddings.py:49`) when `backend="minilm"` is used — triggered at most once per machine, cached to `~/.cache/huggingface/`, and never triggered by the default `"hashing"` backend or on CI."
3. Verify that no other section of `THREAT_MODEL.md` references "single outbound path" or equivalent — if found, update to "two optional outbound paths".

**Relevant Context:**
- `SECURITY.md:23-26` — the paragraph to update
- `docs/security/THREAT_MODEL.md:28-31` — the bullet to update
- `src/cache/embeddings.py:49` — the `load()` call (exact line reference for the threat model citation)
- `src/optimizer/token_counter.py:38-46` — the tiktoken download (existing reference in THREAT_MODEL.md, do not remove)

---

## Ordering and Dependencies

Sub-tasks are independent. Suggested order: 1 → 2 → 3 → 4.

- Sub-task 1 is highest-value (user-facing README).
- Sub-task 2 is the architecture record.
- Sub-task 3 is the ADR amendment (append-only, low risk).
- Sub-task 4 is security/integrity (must not be skipped — would leave a documentation integrity violation).

## Files Changed

| File | Sub-task | Change type |
|------|----------|-------------|
| `README.md` | 1 | Update §8 and §12 |
| `docs/architecture/ARCHITECTURE.md` | 2 | Update §2 and §5 |
| `docs/adr/014-kb-query-embedding-scorer.md` | 3 | Append amendment section |
| `SECURITY.md` | 4 | Update one paragraph |
| `docs/security/THREAT_MODEL.md` | 4 | Update one bullet |

**No new files created.** Five targeted edits to existing documents.
