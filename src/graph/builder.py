"""KnowledgeGraphBuilder — builds a KnowledgeGraph from the KB filesystem.

Parses frontmatter ``related:`` lists and inline ``[text](path)`` markdown links
to produce ``explicit`` edges, then optionally derives ``semantic`` edges from
the :class:`~src.embeddings.index.PersistentEmbeddingIndex`.

This is the only graph module that touches the filesystem or the embedding index.

Design decisions: ADR-017.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from src.graph.graph import KnowledgeGraph
from src.tools.safe_paths import resolve_within  # ATK-FS-01: path containment

if TYPE_CHECKING:
    from src.embeddings.index import PersistentEmbeddingIndex

logger = logging.getLogger(__name__)

# KB category directories (must match PersistentEmbeddingIndex.rebuild() categories)
_CATEGORIES = ("concepts", "guides", "references", "research")

# Regex: YAML frontmatter block (opening --- to closing ---)
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Regex: items under a ``related:`` YAML list (lines starting with ``  - ``)
_RELATED_ITEM_RE = re.compile(r"^\s+-\s+(.+)$", re.MULTILINE)

# Regex: frontmatter scalar fields  ``key: value``
_FM_FIELD_RE = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)

# Regex: frontmatter tag list  ``tags: [a, b, c]``  or  ``tags:\n  - a\n  - b``
_FM_TAGS_INLINE_RE = re.compile(r"^tags:\s*\[(.+)\]$", re.MULTILINE)
_FM_TAGS_BLOCK_RE = re.compile(r"^tags:\s*\n((?:\s+-\s+.+\n?)+)", re.MULTILINE)

# Regex: inline markdown links  ``[text](url_or_path)``
_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


def _parse_frontmatter(content: str) -> Dict[str, Any]:
    """Extract scalar and list fields from YAML frontmatter.

    Returns an empty dict if no frontmatter block is found.
    Only parses: title, date, type, status, tags, related.
    """
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return {}

    fm_text = m.group(1)
    result: Dict[str, Any] = {}

    # Scalar fields
    for key, value in _FM_FIELD_RE.findall(fm_text):
        if key in ("title", "date", "type", "status"):
            result[key] = value.strip().strip('"').strip("'")

    # Tags — inline [a, b, c] or block list
    tags_inline = _FM_TAGS_INLINE_RE.search(fm_text)
    if tags_inline:
        result["tags"] = [t.strip().strip('"').strip("'") for t in tags_inline.group(1).split(",")]
    else:
        tags_block = _FM_TAGS_BLOCK_RE.search(fm_text)
        if tags_block:
            result["tags"] = [
                t.strip().strip('"').strip("'").lstrip("- ")
                for t in _RELATED_ITEM_RE.findall(tags_block.group(1))
            ]

    # Related list (links to other KB docs)
    related_match = re.search(r"^related:\s*\n((?:\s+-\s+.+\n?)+)", fm_text, re.MULTILINE)
    if related_match:
        result["related"] = [
            item.strip() for item in _RELATED_ITEM_RE.findall(related_match.group(1))
        ]

    return result


def _normalise_kb_link(raw_link: str, source_doc_id: str) -> Optional[str]:
    """Convert a raw link path to a KB-relative ``category/filename.md`` key.

    Handles:
    - Absolute KB-relative paths: ``concepts/caching.md``
    - Relative paths with ``../``: ``../concepts/caching.md``
    - Fragment links: ``../concepts/caching.md#section`` → ``concepts/caching.md``

    Returns ``None`` for external URLs or unresolvable paths.
    """
    if raw_link.startswith("http://") or raw_link.startswith("https://"):
        return None  # external URL

    # Strip fragment
    path = raw_link.split("#")[0].strip()
    if not path.endswith(".md"):
        return None  # not a markdown link

    # Resolve relative paths against the source document's directory
    source_parts = source_doc_id.split("/")
    source_dir = "/".join(source_parts[:-1])  # e.g. "concepts"

    if path.startswith("../"):
        # Navigate up from source directory
        segments = (source_dir + "/" + path).split("/")
        normalised_parts: list[str] = []
        for seg in segments:
            if seg == "..":
                if normalised_parts:
                    normalised_parts.pop()
            elif seg and seg != ".":
                normalised_parts.append(seg)
        path = "/".join(normalised_parts)
    elif path.startswith("./"):
        path = (source_dir + "/" + path[2:]).lstrip("/")
    elif "/" not in path:
        # Bare filename — assume same category as source
        path = f"{source_dir}/{path}"

    # Validate: must be category/filename.md
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] in _CATEGORIES:
        return path

    return None


class KnowledgeGraphBuilder:
    """Build a :class:`~src.graph.graph.KnowledgeGraph` from the KB filesystem.

    Args:
        kb_path: Root of the knowledge base (``docs/knowledge-base``).
        index: Optional :class:`~src.embeddings.index.PersistentEmbeddingIndex`
            for semantic edge derivation.  When ``None``, only explicit edges
            are added.
        semantic_threshold: Minimum cosine similarity for a semantic edge
            (default 0.3 per ADR-017 Decision 6).
    """

    def __init__(
        self,
        kb_path: Path,
        index: Optional["PersistentEmbeddingIndex"] = None,
        semantic_threshold: float = 0.3,
    ) -> None:
        self._kb_path = Path(kb_path)
        self._index = index
        self._semantic_threshold = semantic_threshold

    # ---------------------------------------------------------------------- #
    # Public API
    # ---------------------------------------------------------------------- #

    def build(self) -> KnowledgeGraph:
        """Full build: add all nodes, explicit edges, and (if index is set) semantic edges.

        Returns:
            A fully populated :class:`~src.graph.graph.KnowledgeGraph`.
        """
        graph = KnowledgeGraph()
        self._add_nodes(graph)
        explicit_count = self.build_explicit(graph)
        semantic_count = 0
        if self._index is not None:
            semantic_count = self.build_semantic(graph, self._index)

        logger.info(
            "kb_graph_built nodes=%d explicit_edges=%d semantic_edges=%d",
            graph.node_count,
            explicit_count,
            semantic_count,
        )
        return graph

    def build_explicit(self, graph: KnowledgeGraph) -> int:
        """Parse frontmatter ``related:`` lists and inline markdown links → explicit edges.

        Args:
            graph: Graph to populate (nodes must already be added).

        Returns:
            Number of explicit edges added.
        """
        count = 0
        for md_file in self._walk_kb():
            source_doc_id = str(md_file.relative_to(self._kb_path))
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            fm = _parse_frontmatter(content)

            # 1. Frontmatter related: list
            for raw_link in fm.get("related", []):
                target = _normalise_kb_link(raw_link, source_doc_id)
                if target and target != source_doc_id:
                    exists = (self._kb_path / target).exists()
                    graph.add_edge(
                        source_doc_id,
                        target,
                        edge_type="explicit" if exists else "broken",
                        weight=1.0 if exists else 0.0,
                        label=None,
                    )
                    count += 1

            # 2. Inline markdown links
            # Strip frontmatter block before scanning to avoid double-counting
            body = _FRONTMATTER_RE.sub("", content, count=1)
            for link_text, raw_link in _LINK_RE.findall(body):
                target = _normalise_kb_link(raw_link, source_doc_id)
                if target and target != source_doc_id:
                    # Avoid duplicate edges already added from frontmatter
                    existing_targets = {e.target for e in graph.out_edges(source_doc_id)}
                    if target not in existing_targets:
                        exists = (self._kb_path / target).exists()
                        graph.add_edge(
                            source_doc_id,
                            target,
                            edge_type="explicit" if exists else "broken",
                            weight=1.0 if exists else 0.0,
                            label=link_text[:120] if link_text else None,
                        )
                        count += 1

        return count

    # ATK-DOS-02: edge caps prevent edge explosion on mutually-similar corpora.
    _DEFAULT_MAX_EDGES_PER_NODE = 50
    _DEFAULT_MAX_TOTAL_EDGES = 5000

    def build_semantic(
        self,
        graph: KnowledgeGraph,
        index: "PersistentEmbeddingIndex",
        max_edges_per_node: int = _DEFAULT_MAX_EDGES_PER_NODE,
        max_total_edges: int = _DEFAULT_MAX_TOTAL_EDGES,
    ) -> int:
        """Derive semantic edges from the embedding index.

        For each document, queries the index for the top-k most similar chunks.
        Aggregates chunk-level cosine scores to a per-document score using ``max``
        (ADR-017 Decision 2).  Adds a bidirectional semantic edge if the
        aggregated score ≥ ``self._semantic_threshold``.

        ATK-DOS-02: *max_edges_per_node* and *max_total_edges* caps prevent an
        O(N²) edge explosion when many documents are mutually similar.

        Args:
            graph: Graph to populate.
            index: Pre-built :class:`~src.embeddings.index.PersistentEmbeddingIndex`.
            max_edges_per_node: Maximum outbound semantic edges per source node.
            max_total_edges: Global cap on total semantic edges added.

        Returns:
            Number of semantic edges added (each bidirectional pair counts as 1).
        """
        if index.doc_count == 0:
            logger.warning("kb_graph_semantic_skipped: index is empty")
            return 0

        doc_ids = list(self._nodes_from_graph(graph))
        count = 0

        # Build per-document max similarity scores
        # doc_sim[A][B] = max cosine score across all chunk pairs (A_chunk, B_chunk)
        doc_sim: Dict[str, Dict[str, float]] = {d: {} for d in doc_ids}

        for source_id in doc_ids:
            # Read source document content to use as the query
            md_file = self._kb_path / source_id
            if not md_file.exists():
                continue
            # ATK-FS-01: reject symlinks and paths that escape the KB root
            if md_file.is_symlink():
                continue
            try:
                resolve_within(self._kb_path, str(md_file.relative_to(self._kb_path)))
            except ValueError:
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            # Search using the document content as a query — returns chunk-level results
            results: List[Tuple[str, float]] = index.search(content[:4000], top_k=50)

            for chunk_doc_id, score in results:
                # Extract file-level doc_id from chunk id (strip #slug fragment)
                target_id = chunk_doc_id.split("#")[0]
                if target_id == source_id:
                    continue  # skip self-similarity
                if target_id not in doc_sim:
                    continue  # target not in this graph

                # max-aggregation: keep highest chunk score per document pair
                current_best = doc_sim[source_id].get(target_id, 0.0)
                if score > current_best:
                    doc_sim[source_id][target_id] = score

        # Add edges for pairs above threshold (bidirectional), respecting caps
        added_pairs: set = set()
        edges_per_node: Dict[str, int] = {}
        capped = False
        for source_id, targets in doc_sim.items():
            # Sort by score descending to keep the strongest edges under per-node cap
            for target_id, score in sorted(targets.items(), key=lambda x: x[1], reverse=True):
                if score < self._semantic_threshold:
                    continue
                pair = tuple(sorted([source_id, target_id]))
                if pair in added_pairs:
                    continue
                # ATK-DOS-02: check per-node cap
                if edges_per_node.get(source_id, 0) >= max_edges_per_node:
                    continue
                # ATK-DOS-02: check global cap
                if count >= max_total_edges:
                    capped = True
                    break
                added_pairs.add(pair)
                edges_per_node[source_id] = edges_per_node.get(source_id, 0) + 1

                # Bidirectional: add both directions with the same weight
                graph.add_edge(source_id, target_id, "semantic", score)
                graph.add_edge(target_id, source_id, "semantic", score)
                count += 1
            if capped:
                break

        if capped:
            logger.warning(
                "kb_graph_semantic_edge_cap_reached: stopped at %d edges "
                "(max_total_edges=%d, max_edges_per_node=%d)",
                count,
                max_total_edges,
                max_edges_per_node,
            )

        return count

    # ---------------------------------------------------------------------- #
    # Private helpers
    # ---------------------------------------------------------------------- #

    def _add_nodes(self, graph: KnowledgeGraph) -> None:
        """Add all KB documents as nodes, populating props from frontmatter."""
        for md_file in self._walk_kb():
            doc_id = str(md_file.relative_to(self._kb_path))
            content = ""
            try:
                content = md_file.read_text(encoding="utf-8")
                fm = _parse_frontmatter(content)
            except Exception:
                fm = {}

            category = doc_id.split("/")[0] if "/" in doc_id else ""
            try:
                mtime_epoch = md_file.stat().st_mtime
            except OSError:
                mtime_epoch = 0.0

            graph.add_node(
                doc_id,
                title=fm.get("title", _extract_h1(content)),
                category=category,
                tags=fm.get("tags", []),
                date=fm.get("date", ""),
                type=fm.get("type", ""),
                status=fm.get("status", ""),
                mtime_epoch=mtime_epoch,
                content_length=len(content),
                description=_extract_description(content),
                related_refs=fm.get("related", []),
            )

    def _walk_kb(self):
        """Yield all ``*.md`` files across the four KB category directories.

        ATK-FS-01: symlinks and paths that escape the KB root are silently
        skipped so callers (_add_nodes, _build_explicit_edges) never open
        adversarially-crafted files.
        """
        for cat in _CATEGORIES:
            cat_path = self._kb_path / cat
            if not cat_path.exists():
                continue
            for md_file in sorted(cat_path.glob("*.md")):
                if md_file.is_symlink():
                    continue
                try:
                    resolve_within(self._kb_path, str(md_file.relative_to(self._kb_path)))
                except ValueError:
                    continue
                yield md_file

    @staticmethod
    def _nodes_from_graph(graph: KnowledgeGraph) -> List[str]:
        """Return all doc_ids from the graph."""
        return [doc_id for doc_id, _ in graph.nodes()]


def _extract_h1(content: str) -> str:
    """Extract the ``# Title`` line from a markdown document."""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def _extract_description(content: str) -> str:
    """Extract the first non-heading, non-blank paragraph from *content*.

    Strips the YAML frontmatter block first, then skips blank lines and lines
    that start with ``#``.  Returns the first non-empty paragraph truncated to
    200 characters.  Returns ``""`` if nothing qualifies.

    Args:
        content: Raw Markdown document text.

    Returns:
        A short description string (≤ 200 chars) or ``""``.
    """
    # Strip frontmatter
    text = _FRONTMATTER_RE.sub("", content, count=1)

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue  # blank line
        if stripped.startswith("#"):
            continue  # heading
        if stripped.startswith("|"):
            continue  # table row
        if stripped.startswith("```") or stripped.startswith("~~~"):
            continue  # code fence
        if stripped.startswith(">"):
            continue  # blockquote preamble
        # First qualifying line
        return stripped[:200]
    return ""


def build_graph_metadata(
    kb_path: Path,
    semantic_threshold: float,
    built_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Produce the ``metadata`` dict written alongside the graph in ``kb-graph.json``."""
    return {
        "built_at": built_at or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "kb_path": str(kb_path),
        "semantic_threshold": semantic_threshold,
    }
