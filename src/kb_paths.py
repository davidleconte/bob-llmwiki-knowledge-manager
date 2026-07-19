"""Canonical resolution of on-disk KB artifact paths (CODE-04 / W2-2d).

All writers (``KBIndexer``, ``graph-build``, ``kb-status``) and readers
(``kb-search``, the research agent) must resolve the embedding-index and graph
locations the *same* way. When they do not, the writer populates one directory
while the reader looks in another — which is exactly why the CODE-02 retrieval
stack silently fell back to keyword-only in the default layout: readers used
``kb_path.parent/.bob/kb-index`` (``docs/.bob/kb-index``) while the index is
written to the repo-root ``.bob/kb-index``.

The ``.bob/`` directory is a repo-root convention (alongside ``.bob/settings.json``,
``.bob/kb-graph.json``), so both artifacts are anchored at the KB's repo root,
discovered by walking up from the KB path for a ``.bob/`` or ``.git/`` marker.
This is CWD-independent and matches where the artifacts actually live.
"""

from __future__ import annotations

from pathlib import Path

_BOB_DIR = ".bob"
INDEX_DIRNAME = "kb-index"
GRAPH_FILENAME = "kb-graph.json"


def repo_root_for(kb_path: Path) -> Path:
    """Nearest ancestor of *kb_path* containing a ``.bob/`` or ``.git/`` marker.

    Falls back to the KB's parent directory (the conventional
    ``<root>/docs/knowledge-base`` layout) when no marker is found, so resolution
    never raises and always yields a deterministic location.
    """
    p = Path(kb_path).resolve()
    for anc in (p, *p.parents):
        if (anc / _BOB_DIR).is_dir() or (anc / ".git").is_dir():
            return anc
    return p.parent


def resolve_index_path(kb_path: Path) -> Path:
    """Canonical embedding-index directory: ``<repo-root>/.bob/kb-index``."""
    return repo_root_for(kb_path) / _BOB_DIR / INDEX_DIRNAME


def resolve_graph_path(kb_path: Path) -> Path:
    """Canonical knowledge-graph file: ``<repo-root>/.bob/kb-graph.json``."""
    return repo_root_for(kb_path) / _BOB_DIR / GRAPH_FILENAME
