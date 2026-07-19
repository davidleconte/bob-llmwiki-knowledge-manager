"""ATK-MEM-05 regression: graph poisoning via author-controlled explicit edges.

A crafted document controls its frontmatter ``related:`` list and inline links.
Before the fix the explicit-edge path had no cap, no dedup, and no trust check,
so one document could:
  * mint unbounded edges (skewing PageRank / hub metrics),
  * mint duplicate parallel edges to the same target, and
  * pull a quarantined document into the graph.

RED on the unfixed builder (200 edges from one node; 10 parallel dupes;
quarantined doc present), GREEN once explicit edges are capped + de-duped and
quarantined docs are excluded.
"""
from pathlib import Path

from src.graph.builder import KnowledgeGraphBuilder
from src.graph.graph import KnowledgeGraph

# Expected per-source explicit-edge cap (mirrors builder._MAX_EXPLICIT_EDGES_PER_NODE).
# Hardcoded rather than imported so this test exercises the *behaviour* on an
# unfixed tree (which lacks the constant) instead of failing at import.
EXPECTED_CAP = 50


def _make_kb(root: Path) -> Path:
    kb = root / "kb"
    for cat in ("concepts", "guides", "references", "research"):
        (kb / cat).mkdir(parents=True)
    return kb


def _write(kb: Path, cat: str, name: str, content: str) -> Path:
    p = kb / cat / name
    p.write_text(content, encoding="utf-8")
    return p


def _doc_with_related(targets, title="Source"):
    lines = "\n".join(f"  - {t}" for t in targets)
    return f"---\ntitle: {title}\nrelated:\n{lines}\n---\n\n# {title}\n\nbody text here\n"


def test_explicit_edges_are_capped_per_source(tmp_path):
    kb = _make_kb(tmp_path)
    targets = [f"concepts/t{i:03d}.md" for i in range(200)]
    _write(kb, "concepts", "source.md", _doc_with_related(targets))

    graph = KnowledgeGraphBuilder(kb).build()
    out = graph.out_edges("concepts/source.md")
    assert len(out) == EXPECTED_CAP, len(out)  # 200 unique → capped at 50


def test_duplicate_related_targets_are_deduped(tmp_path):
    kb = _make_kb(tmp_path)
    _write(kb, "concepts", "dup.md", "---\ntitle: Dup\n---\n\n# Dup\n\nreal target\n")
    _write(kb, "concepts", "source.md", _doc_with_related(["concepts/dup.md"] * 10))

    builder = KnowledgeGraphBuilder(kb)
    graph = KnowledgeGraph()
    builder._add_nodes(graph)
    added = builder.build_explicit(graph)

    out = [e for e in graph.out_edges("concepts/source.md") if e.target == "concepts/dup.md"]
    assert len(out) == 1, out
    assert added == 1, added  # returned count must reflect the dedup, not 10


def test_quarantined_doc_is_excluded_from_graph(tmp_path):
    kb = _make_kb(tmp_path)
    # A verified doc links to a quarantined doc, which links back.
    _write(
        kb,
        "concepts",
        "good.md",
        "---\ntitle: Good\ntrust_tier: verified\nrelated:\n  - references/evil.md\n---\n\n# Good\n",
    )
    _write(
        kb,
        "references",
        "evil.md",
        "---\ntitle: Evil\ntrust_tier: quarantined\nrelated:\n  - concepts/good.md\n---\n\n# Evil\n",
    )

    graph = KnowledgeGraphBuilder(kb).build()
    node_ids = {doc_id for doc_id, _ in graph.nodes()}

    assert "references/evil.md" not in node_ids, node_ids
    assert graph.get_node("references/evil.md") is None
    # No edge references the quarantined doc, and it has no PageRank mass.
    assert all(e.target != "references/evil.md" for e in graph.out_edges("concepts/good.md"))
    assert "references/evil.md" not in graph.pagerank()
