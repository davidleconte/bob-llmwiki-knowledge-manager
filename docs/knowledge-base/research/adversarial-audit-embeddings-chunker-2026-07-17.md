---
title: "Adversarial Audit — src/embeddings/ chunker integration (2026-07-17)"
date: 2026-07-17
type: research
status: complete
severity: critical
tags: [adversarial-audit, embeddings, chunker, index, bug, fix-required]
related:
  - ../concepts/kb-tos-embedding-layer.md
  - ../guides/kb-tos-integration-roadmap.md
  - ../research/kb-tos-integration-feasibility-2026-07-14.md
  - ../../../src/embeddings/index.py
  - ../../../src/embeddings/chunker.py
  - ../../../src/embeddings/indexer.py
---

# Adversarial Audit — `src/embeddings/` Chunker Integration (2026-07-17)

**Scope:** `src/embeddings/index.py` (externally modified), `src/embeddings/chunker.py`,
`src/embeddings/indexer.py`  
**Method:** Live code execution, direct probe scripts, manifest/matrix inspection  
**Baseline:** All 69 tests in `tests/embeddings/` + `tests/tools/test_kb_query.py` pass  

---

## Summary

The `MarkdownChunker` integration introduced a **critical data-corruption bug** (AF-1)
that silently prevents the persistent index from ever loading after its first flush.
Every call to `rebuild()` + `flush()` writes an index whose `vectors.npy` row count
mismatches its `manifest.json` entry count; `FileBackedVectorStore.load()` detects
the mismatch, logs a warning, and returns `None` — making the persistence layer
permanently inert. A second critical bug (AF-2) means `is_stale()` always returns
`True` for any non-default KB path, forcing a full re-index on every call.

---

## Finding AF-1 — **CRITICAL: `flush()` writes a mismatched manifest, breaking every reload**

### Root cause

`rebuild()` stores mtime/hash staleness metadata under two kinds of keys in `self._manifest`:

- **Chunk keys** (e.g. `concepts/a.md#section-one`) — added by `index_document()` as vector rows
- **File keys** (e.g. `concepts/a.md`) — added by `rebuild()` as staleness sentinels with `{"path":…, "mtime":…, "hash":…}`

When `flush()` calls `self._store.save(…, self._matrix, self._manifest)`, the matrix
has **N chunk rows** but the manifest has **N chunks + F files** entries (where F = number
of indexed files). `FileBackedVectorStore.load()` enforces:

```python
if matrix.ndim != 2 or matrix.shape[0] != len(manifest):
    logger.warning("kb_index_shape_mismatch …")
    return None
```

**Measured:** One file producing one chunk → matrix shape `(1, 1000)`, manifest entries `2`.
Two files producing two chunks → matrix shape `(2, 1000)`, manifest entries `3` (one extra per file).
`load()` returns `None` in all cases. The index is written but never read back.

### Impact

- **Persistence is completely broken** — every Bob Shell session re-indexes the entire KB from scratch
- The 69 existing tests do not catch this because `test_flush_and_reload` calls `index_document()` directly (which does not add file-level keys) and never calls `rebuild()` + `flush()` + reload
- The `rebuild_incremental_skips_unchanged` test passes because it calls `rebuild()` twice on the *same in-memory instance*, never reloading from disk

### Verified

```
Matrix shape: (1, 1000)
Manifest entries: 2 (concepts/a.md#section-one, concepts/a.md)
load() returns None: True
```

### Fix

Separate the two manifest roles. The simplest correct fix: use a **separate side-file**
(`staleness.json`) for file-level mtime/hash sentinels; keep `manifest.json` holding
**only chunk-level entries** (one per vector row). `FileBackedVectorStore` then
correctly enforces `matrix.shape[0] == len(manifest)`.

Alternative (lower blast-radius): strip file-level keys from the manifest before
passing it to `self._store.save()`, then reload them from a separate data structure
or re-derive them at startup.

---

## Finding AF-2 — **CRITICAL: `is_stale()` always returns `True` for non-default KB paths**

### Root cause

`is_stale()` derives the key to look up in the manifest with:

```python
kb_root = self._index_path.parent.parent  # .bob/ → repo root
raw_id = str(doc_path.relative_to(kb_root / "docs/knowledge-base"))
```

This hardcodes the KB location as `<repo-root>/docs/knowledge-base`. When a test (or
any caller) uses a temporary path like `/tmp/abc/kb/concepts/a.md`, the `relative_to()`
call raises `ValueError` and the except clause falls back to `raw_id = str(doc_path)` —
the **absolute path string**. That string is never in the manifest (which stores
KB-relative paths like `concepts/a.md`). `self._manifest.get(file_doc_id)` returns
`None`, and `is_stale()` returns `True` unconditionally.

**Measured:**  
```
doc:     /tmp/.../kb/concepts/a.md
fallback raw_id: /tmp/.../kb/concepts/a.md
manifest keys:   ['concepts/a.md#section-one', 'concepts/a.md']
key in manifest: False
is_stale(unchanged): True
is_stale(changed):   True
```

### Impact

- Any caller using a custom `kb_path` (all test scenarios, non-default install locations,
  CI environments) will get `is_stale() == True` on every file, forcing a full re-index
  on every `rebuild()` call — defeating the incremental update design entirely
- The `is_stale` behaviour is masked in tests because tests call `rebuild()` directly
  and never exercise `is_stale()` with a real tmp path against the manifest

### Fix

`is_stale()` should compute the key by asking the `PersistentEmbeddingIndex` about the
`kb_path` it was given at construction (or passed in), not by reconstructing it from
the index path. Pass `kb_path` explicitly:

```python
def is_stale(self, doc_path: Path, kb_path: Path) -> bool:
    file_doc_id = str(doc_path.relative_to(kb_path)).split("#")[0]
    ...
```

Or store `self._kb_path` at construction and use it here.

---

## Finding AF-3 — **Medium: `_extract_tables` uses `findall` as a guard then `finditer` for results — `findall` returns the last captured group row, not the full table**

### Root cause

`_TABLE_RE = re.compile(r"(\|.+\n)+", re.MULTILINE)` uses a capturing group `(…)+`.
`findall` with a capturing group returns **the last captured repetition from each match**,
not the full match. For a 3-row table, `findall` returns `['| row3 |\n']` — a single
string with only the last row.

The guard `if not tables: return` is **correct** (empty list is a reliable no-table
signal). But `len(tables)` is **not a reliable table count** — it returns the correct
number of tables (since there's one captured group per table match), but each element
is the last row rather than the full table. This is only used as a truthy guard, so
the functional behaviour is correct.

However, the pattern is misleading and fragile: a future developer who adds
`for table_text in tables:` (instead of using `finditer`) would get truncated text.

### Impact

Current behaviour: correct (guard only). Future maintenance risk: high (confusing pattern).

### Fix (Low priority)

Replace `findall` with a direct `finditer` emptiness check:

```python
matches = list(_TABLE_RE.finditer(body))
if not matches:
    return
for i, match in enumerate(matches):
    ...
```

---

## Finding AF-4 — **Medium: `KBIndexer.query()` accesses `self._index._embedder` (private attribute)**

`KBIndexer.query()` at line 94 does `embedder=self._index._embedder` — accessing
the `_embedder` private attribute of `PersistentEmbeddingIndex`. This bypasses
encapsulation and creates a fragile coupling: a rename of `_embedder` silently breaks
`KBIndexer.query()` at runtime with no static analysis warning.

### Fix (Low priority)

Expose a public property: `PersistentEmbeddingIndex.embedder` and use it in `KBIndexer`.

---

## Finding AF-5 — **Low: `doc_count` counts only chunk IDs, documentation says "documents"**

The docstring for `doc_count` says "Number of documents currently in the in-memory
index." After the chunker integration, `doc_count` actually counts **chunks**
(e.g. `concepts/a.md#section-one`), not documents. A 2-section file produces 2 entries.

This misleads callers who interpret `doc_count` as a file count. `KnowledgeBaseQuery.query()`
uses `if self._index is not None and self._index.doc_count > 0` — this still works
correctly (any chunks → use fast path) but the semantics are wrong.

### Fix

Rename to `chunk_count` or update the docstring to say "Number of indexed chunks".

---

## Finding AF-6 — **Low: `test_flush_and_reload` does not exercise the `rebuild()` path**

`test_flush_and_reload` calls `idx1.index_document(…)` directly, not `rebuild()`.
This bypasses the file-level manifest key insertion that `rebuild()` adds, so it
never triggers AF-1. The test gives false confidence that persistence works.

A test exercising the full `rebuild() → flush() → new_instance.search()` round-trip
is missing — this is the exact path that fails in production.

---

## Test coverage gap

| Scenario | Tested | Covers AF |
|---|---|---|
| `index_document()` → `flush()` → reload | ✅ `test_flush_and_reload` | ❌ Bypasses AF-1 |
| `rebuild()` → `flush()` → new instance → `search()` | ❌ Missing | ✅ Would catch AF-1 |
| `is_stale()` with tmp path | ❌ Missing | ✅ Would catch AF-2 |
| `is_stale()` with default `docs/knowledge-base` path | ❌ Missing | Partial AF-2 |

---

## Verdict

| Finding | Severity | Status |
|---|---|---|
| AF-1: flush/reload manifest mismatch (chunker adds file-level keys) | 🔴 Critical | Fix required |
| AF-2: `is_stale()` always True for non-default kb_path | 🔴 Critical | Fix required |
| AF-3: `findall` in `_extract_tables` guard returns last captured group | 🟡 Medium | Low-risk refactor |
| AF-4: `KBIndexer.query()` accesses `_embedder` private attribute | 🟡 Medium | Minor encapsulation fix |
| AF-5: `doc_count` counts chunks, not documents | 🟢 Low | Docstring update |
| AF-6: `test_flush_and_reload` does not exercise rebuild path | 🟢 Low | Add regression test |

**Persistence is currently completely broken for any non-trivial KB.** AF-1 and AF-2
must be fixed before the `src/embeddings/` layer has any practical value.

---

*Last Updated: 2026-07-17*
*Category: Research*
*Status: Complete — AF-1 and AF-2 require immediate fixes*
