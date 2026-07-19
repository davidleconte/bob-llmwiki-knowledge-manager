#!/usr/bin/env python3
"""Manifest-backed retrieval p@3 measurement (CLM-06).

Replaces the un-provenanced, hardcoded ``p@3=0.88`` with a reproducible number:
builds the real embedding index + knowledge graph over ``docs/knowledge-base``,
runs the wired :class:`KnowledgeBaseQuery` (embedding_weight=0.7, graph_weight=0.3
per ADR-017) over a committed golden set, and writes ``report.json`` +
``manifest.json`` with the same reproducibility provenance as the savings harness.

p@3 here = fraction of golden queries whose single expected document appears among
the top-3 *distinct* documents returned (a hit-rate@3 over one relevant doc each).

Usage::

    python evaluation/scripts/score_retrieval.py            # writes a dated report
    python evaluation/scripts/score_retrieval.py --json     # + machine report to stdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cache.embeddings import EmbeddingGenerator  # noqa: E402
from src.embeddings.index import PersistentEmbeddingIndex  # noqa: E402
from src.embeddings.indexer import KBIndexer  # noqa: E402
from src.graph.builder import KnowledgeGraphBuilder  # noqa: E402
from src.tools.kb_query import KnowledgeBaseQuery  # noqa: E402
from src.validation.manifest import build_manifest  # noqa: E402

KB_PATH = REPO_ROOT / "docs" / "knowledge-base"
GOLDEN_SET = REPO_ROOT / "evaluation" / "data" / "retrieval_golden_set.json"
EMBEDDING_WEIGHT = 0.7  # ADR-017
GRAPH_WEIGHT = 0.3      # ADR-017
SEED = 0


def _data_hash(golden: Dict[str, Any]) -> str:
    """sha256 over the golden set + the exact corpus it is scored against."""
    h = hashlib.sha256()
    h.update(json.dumps(golden, sort_keys=True).encode("utf-8"))
    for md in sorted(KB_PATH.rglob("*.md")):
        h.update(md.relative_to(KB_PATH).as_posix().encode("utf-8"))
        h.update(md.read_bytes())
    return h.hexdigest()[:16]


def _top_distinct_docs(results: List[Dict[str, Any]], k: int) -> List[str]:
    """Top-k distinct document ids (strip the ``#slug`` chunk fragment, keep order)."""
    seen: List[str] = []
    for r in results:
        doc = str(r.get("file", "")).split("#")[0]
        if doc and doc not in seen:
            seen.append(doc)
        if len(seen) >= k:
            break
    return seen


def _score(kbq: KnowledgeBaseQuery, queries: List[Dict[str, Any]], k: int) -> Dict[str, Any]:
    hits = 0
    per_query: List[Dict[str, Any]] = []
    for entry in queries:
        q = entry["query"]
        expected = entry["expected_doc_id"]
        results = kbq.query(q, max_results=max(k, 10)).get("results", [])
        top = _top_distinct_docs(results, k)
        hit = expected in top
        hits += int(hit)
        per_query.append({"query": q, "expected": expected, "top_k": top, "hit": hit})
    n = len(queries)
    return {"p_at_k": round(hits / n, 4) if n else 0.0, "hits": hits, "n": n, "per_query": per_query}


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manifest-backed retrieval p@3 (CLM-06).")
    parser.add_argument("--json", action="store_true", help="print machine report to stdout")
    parser.add_argument("--out-dir", default=None, help="output directory for report/manifest")
    args = parser.parse_args(argv)

    golden = json.loads(GOLDEN_SET.read_text(encoding="utf-8"))
    k = int(golden.get("k", 3))
    queries = golden["queries"]

    embedder = EmbeddingGenerator()
    with tempfile.TemporaryDirectory() as tmp:
        index = PersistentEmbeddingIndex(embedder, index_path=Path(tmp) / "kb-index")
        KBIndexer(KB_PATH, index).sync()
        graph = KnowledgeGraphBuilder(KB_PATH, index=index).build()

        wired = _score(
            KnowledgeBaseQuery(
                str(KB_PATH),
                index=index,
                graph=graph,
                embedding_weight=EMBEDDING_WEIGHT,
                graph_weight=GRAPH_WEIGHT,
            ),
            queries,
            k,
        )
        keyword = _score(
            KnowledgeBaseQuery(str(KB_PATH), embedding_weight=0.0, graph_weight=0.0),
            queries,
            k,
        )

    manifest = build_manifest(
        config={
            "embedding_weight": EMBEDDING_WEIGHT,
            "graph_weight": GRAPH_WEIGHT,
            "embedding_backend": embedder._backend,
            "k": k,
        },
        data_hash=_data_hash(golden),
        seed=SEED,
        model=f"{embedder._backend}-embeddings",
        tiktoken_active=False,
        repo_root=REPO_ROOT,
        extra={"corpus": "docs/knowledge-base", "n_queries": len(queries), "n_docs": len(list(KB_PATH.rglob("*.md")))},
    )

    report = {
        "metric": "p_at_3",
        "k": k,
        "p_at_3_wired": wired["p_at_k"],
        "p_at_3_keyword_baseline": keyword["p_at_k"],
        "hits_wired": wired["hits"],
        "hits_keyword": keyword["hits"],
        "n_queries": wired["n"],
        "per_query": wired["per_query"],
        "manifest": manifest,
    }

    out_dir = Path(args.out_dir) if args.out_dir else (
        REPO_ROOT / "evaluation" / "results" / "retrieval-2026-07-19"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(
        f"p@{k} (wired w=0.7): {wired['p_at_k']:.4f} ({wired['hits']}/{wired['n']})  |  "
        f"keyword baseline: {keyword['p_at_k']:.4f} ({keyword['hits']}/{keyword['n']})\n"
        f"report + manifest written to {out_dir.relative_to(REPO_ROOT)}"
    )
    if args.json:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
