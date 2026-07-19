# kb_paths

Canonical resolution of on-disk KB artifact paths (CODE-04 / W2-2d).

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

## Constants

- `_BOB_DIR`
- `INDEX_DIRNAME`
- `GRAPH_FILENAME`

## Functions

### `repo_root_for(kb_path: Path) -> Path`

Nearest ancestor of *kb_path* containing a ``.bob/`` or ``.git/`` marker.

Falls back to the KB's parent directory (the conventional
``<root>/docs/knowledge-base`` layout) when no marker is found, so resolution
never raises and always yields a deterministic location.


### `resolve_index_path(kb_path: Path) -> Path`

Canonical embedding-index directory: ``<repo-root>/.bob/kb-index``.


### `resolve_graph_path(kb_path: Path) -> Path`

Canonical knowledge-graph file: ``<repo-root>/.bob/kb-graph.json``.

