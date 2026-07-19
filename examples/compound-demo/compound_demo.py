#!/usr/bin/env python3
"""Reproducible two-session write→retrieve→compound demo (D3 / MEM-13).

The headline "prove it compounds" deliverable. Session 1 analyzes the pinned
fixture repo and writes signed ``generated`` KB docs; session 2 issues a query
that must retrieve one of session 1's findings — the reproducible proof that what
one session learns is available to the next, rather than being re-derived.

The fixture is vendored under ``examples/compound-demo/fixture-repo`` (inside the
repo, so path containment holds without ``--allow-external``). Run from the repo
root::

    python examples/compound-demo/compound_demo.py

Exits 0 and prints a manifest (session-1 output ids, index chunk count, session-2
retrieved ids, the matched intersection, code SHA) when compounding is
demonstrated; exits 1 if session 2 surfaces no session-1 finding.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

DEMO_DIR = Path(__file__).resolve().parent
FIXTURE = DEMO_DIR / "fixture-repo"
# A query built from the fixture's own subject matter (an auth module with a
# plaintext-password weakness). The demo KB holds only session-1 output, so any
# retrieval is a session-1 finding — the manifest records exactly which.
SESSION2_QUERY = "authentication login password security weakness findings"


def _code_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(DEMO_DIR),
            capture_output=True,
            text=True,
            check=False,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def run_compound_demo(
    kb_dir: Path,
    fixture: Path = FIXTURE,
    query: str = SESSION2_QUERY,
    code_sha: Optional[str] = None,
) -> Dict[str, Any]:
    """Run session 1 (analyze→write) then session 2 (query→retrieve); return a manifest.

    Args:
        kb_dir: Fresh KB directory to write session-1 output into and index for
            session-2 retrieval.
        fixture: The pinned fixture repo to analyze (must be inside cwd).
        query: The session-2 retrieval query.
        code_sha: Override the recorded code SHA (defaults to ``git rev-parse HEAD``).
    """
    from src.cache.embeddings import EmbeddingGenerator
    from src.delegation.pipeline import analyze_and_ingest
    from src.embeddings.index import PersistentEmbeddingIndex
    from src.embeddings.indexer import KBIndexer
    from src.tools.kb_query import KnowledgeBaseQuery

    kb_dir = Path(kb_dir)
    research = kb_dir / "research"
    research.mkdir(parents=True, exist_ok=True)

    # The pipeline contains target_dir within cwd, so pass a cwd-relative path.
    rel_fixture = fixture.resolve().relative_to(Path.cwd())

    # --- Session 1: analyze the fixture, write generated findings into the KB. ---
    res1 = analyze_and_ingest(
        target_dir=str(rel_fixture),
        kb_path=str(kb_dir),
        output_dir=str(research),
        max_workers=5,
        depth="shallow",
        compress=False,
    )
    kb_resolved = kb_dir.resolve()
    session1_ids = sorted(
        str(Path(f).resolve().relative_to(kb_resolved)) for f in res1.output_files
    )

    # --- Session 2: a fresh index + query must surface a session-1 finding. ---
    idx = PersistentEmbeddingIndex(EmbeddingGenerator(), index_path=kb_dir / ".idx")
    chunk_count = KBIndexer(kb_dir, idx).sync()
    kbq = KnowledgeBaseQuery(str(kb_dir), index=idx, embedding_weight=0.7)
    result = kbq.query(query, include_content=False)
    # Strip any chunk ``#slug`` fragment so retrieved ids compare to file-level ids.
    retrieved = [h["file"].split("#")[0] for h in result.get("results", []) if h.get("file")]
    # Preserve retrieval order while de-duplicating.
    retrieved = list(dict.fromkeys(retrieved))
    matched = sorted(set(session1_ids) & set(retrieved))

    return {
        "demo": "compound-write-retrieve",
        "code_sha": code_sha or _code_sha(),
        "fixture": str(rel_fixture),
        "session1_output_ids": session1_ids,
        "session1_docs_written": len(session1_ids),
        "index_chunk_count": chunk_count,
        "session2_query": query,
        "session2_retrieved_ids": retrieved,
        "matched_ids": matched,
        "compounded": bool(matched),
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        manifest = run_compound_demo(Path(tmp) / "kb")
    print(json.dumps(manifest, indent=2))
    if not manifest["compounded"]:
        print(
            "❌ compounding NOT demonstrated: session 2 retrieved no session-1 finding",
            file=sys.stderr,
        )
        return 1
    print(f"✅ compounding demonstrated: session 2 retrieved {manifest['matched_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
