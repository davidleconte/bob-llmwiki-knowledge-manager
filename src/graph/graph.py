"""Knowledge graph core — in-memory property graph over KB documents.

Nodes represent source files at ``category/filename.md`` granularity.
Edges are either ``explicit`` (author-stated: frontmatter ``related:`` or inline
markdown links) or ``semantic`` (similarity-derived from the embedding index).

All methods are pure — no filesystem I/O, no embedding computation.
I/O is handled by :class:`~src.graph.store.GraphStore`.
Building is handled by :class:`~src.graph.builder.KnowledgeGraphBuilder`.

Design decisions: ADR-017 (``docs/adr/017-knowledge-graph-layer.md``).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Data types
# --------------------------------------------------------------------------- #


@dataclass
class NodeProps:
    """Properties attached to a KB document node.

    All fields are optional so callers can add nodes with partial metadata.
    Defaults ensure the graph is always traversable even on partial data.

    P4 additions (backward-compatible — old ``kb-graph.json`` files load cleanly):
        mtime_epoch: File modification time as a Unix epoch float (0.0 = unknown).
        content_length: Document character count (0 = unknown).
        description: First non-heading paragraph, ≤ 200 chars (empty = none found).
        related_refs: Raw ``related:`` list from frontmatter (strings, not resolved).
    """

    title: str = "Untitled"
    category: str = ""
    tags: List[str] = field(default_factory=list)
    date: str = ""
    type: str = ""
    status: str = ""
    # P4 fields — all optional with safe defaults
    mtime_epoch: float = 0.0
    content_length: int = 0
    description: str = ""
    related_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "category": self.category,
            "tags": self.tags,
            "date": self.date,
            "type": self.type,
            "status": self.status,
            "mtime_epoch": self.mtime_epoch,
            "content_length": self.content_length,
            "description": self.description,
            "related_refs": self.related_refs,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NodeProps":
        return cls(
            title=d.get("title", "Untitled"),
            category=d.get("category", ""),
            tags=d.get("tags", []),
            date=d.get("date", ""),
            type=d.get("type", ""),
            status=d.get("status", ""),
            mtime_epoch=float(d.get("mtime_epoch", 0.0)),
            content_length=int(d.get("content_length", 0)),
            description=d.get("description", ""),
            related_refs=d.get("related_refs", []),
        )


@dataclass
class Edge:
    """A directed, weighted, typed edge between two KB document nodes.

    Edge types:
        ``explicit``  — author-stated (frontmatter ``related:`` or inline link)
        ``semantic``  — similarity-derived (cosine ≥ threshold)
        ``broken``    — explicit link whose target file does not exist

    Weight:
        Explicit/broken edges carry ``weight = 1.0`` (or ``0.0`` for broken).
        Semantic edges carry the cosine similarity score ∈ (threshold, 1.0].
    """

    source: str
    target: str
    type: str  # "explicit" | "semantic" | "broken"
    weight: float
    label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "weight": self.weight,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Edge":
        return cls(
            source=d["source"],
            target=d["target"],
            type=d["type"],
            weight=float(d.get("weight", 1.0)),
            label=d.get("label"),
        )


# --------------------------------------------------------------------------- #
# KnowledgeGraph
# --------------------------------------------------------------------------- #


class KnowledgeGraph:
    """In-memory property graph over KB documents.

    **Nodes** — ``category/filename.md`` keys with :class:`NodeProps`.
    **Edges** — directed, weighted, typed; stored in an adjacency list
    (``source → list[Edge]``) and a reverse index (``target → list[Edge]``)
    for O(1) inbound-edge lookup.

    All public methods are pure (no I/O).

    Thread-safety: not thread-safe; build once, then read-only.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, NodeProps] = {}
        # Outbound adjacency: source → [Edge, ...]
        self._out: Dict[str, List[Edge]] = {}
        # Inbound adjacency: target → [Edge, ...]
        self._in: Dict[str, List[Edge]] = {}

    # ---------------------------------------------------------------------- #
    # Mutation
    # ---------------------------------------------------------------------- #

    def add_node(self, doc_id: str, **props: Any) -> None:
        """Add or update a node.

        Args:
            doc_id: KB-relative file path (e.g. ``concepts/caching.md``).
            **props: Keyword arguments forwarded to :class:`NodeProps`.
        """
        if doc_id not in self._nodes:
            self._out[doc_id] = []
            self._in[doc_id] = []
        self._nodes[doc_id] = NodeProps(
            **{k: v for k, v in props.items() if k in NodeProps.__dataclass_fields__}
        )

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: str,
        weight: float = 1.0,
        label: Optional[str] = None,
    ) -> None:
        """Add a directed edge from *source* to *target*.

        Auto-creates node stubs if either endpoint is not yet in the graph.

        Args:
            source: Source doc_id.
            target: Target doc_id.
            edge_type: ``"explicit"``, ``"semantic"``, or ``"broken"``.
            weight: Edge weight (0.0–1.0 for semantic; 1.0 for explicit; 0.0 for broken).
            label: Optional human-readable label (link text for explicit edges).
        """
        if source not in self._nodes:
            self.add_node(source)
        if target not in self._nodes:
            self.add_node(target)

        edge = Edge(source=source, target=target, type=edge_type, weight=weight, label=label)
        self._out[source].append(edge)
        self._in[target].append(edge)

    # ---------------------------------------------------------------------- #
    # Properties
    # ---------------------------------------------------------------------- #

    @property
    def node_count(self) -> int:
        """Number of nodes in the graph."""
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        """Total number of edges (all types) in the graph."""
        return sum(len(edges) for edges in self._out.values())

    def nodes(self) -> Iterable[Tuple[str, NodeProps]]:
        """Iterate over (doc_id, props) pairs."""
        return self._nodes.items()

    def out_edges(self, doc_id: str) -> List[Edge]:
        """Outbound edges from *doc_id*."""
        return self._out.get(doc_id, [])

    def in_edges(self, doc_id: str) -> List[Edge]:
        """Inbound edges into *doc_id*."""
        return self._in.get(doc_id, [])

    def get_node(self, doc_id: str) -> Optional[NodeProps]:
        """Return the :class:`NodeProps` for *doc_id*, or ``None`` if absent."""
        return self._nodes.get(doc_id)

    # ---------------------------------------------------------------------- #
    # Traversal
    # ---------------------------------------------------------------------- #

    def neighbours(
        self,
        doc_id: str,
        depth: int = 1,
        edge_types: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """BFS neighbourhood of *doc_id* up to *depth* hops.

        Returns a dict mapping each reachable doc_id (excluding *doc_id*
        itself) to ``{"distance": int, "edges": [Edge]}``.

        Args:
            doc_id: Starting node.
            depth: Number of hops (1 = direct neighbours only).
            edge_types: Restrict traversal to these edge types. ``None`` = all types.

        Returns:
            ``{doc_id: {"distance": int, "edges": [Edge]}}``
        """
        if doc_id not in self._nodes:
            return {}

        visited: Dict[str, Dict[str, Any]] = {}
        queue: deque[Tuple[str, int]] = deque([(doc_id, 0)])
        seen = {doc_id}

        while queue:
            current, dist = queue.popleft()
            if dist >= depth:
                continue
            for edge in self._out.get(current, []):
                if edge_types is not None and edge.type not in edge_types:
                    continue
                neighbour = edge.target
                if neighbour not in seen:
                    seen.add(neighbour)
                    visited[neighbour] = {"distance": dist + 1, "edges": [edge]}
                    queue.append((neighbour, dist + 1))
                else:
                    # Record additional edges to already-visited nodes
                    visited[neighbour]["edges"].append(edge)

        return visited

    def path(self, source: str, target: str) -> Optional[List[str]]:
        """Shortest path from *source* to *target* (BFS, unweighted).

        Returns a list of doc_ids from *source* to *target* inclusive,
        or ``None`` if no path exists.

        Args:
            source: Start node doc_id.
            target: End node doc_id.
        """
        if source not in self._nodes or target not in self._nodes:
            return None
        if source == target:
            return [source]

        parents: Dict[str, Optional[str]] = {source: None}
        queue: deque[str] = deque([source])

        while queue:
            node = queue.popleft()
            if node == target:
                # Reconstruct path
                path: List[str] = []
                current: Optional[str] = target
                while current is not None:
                    path.append(current)
                    current = parents[current]
                path.reverse()
                return path
            for edge in self._out.get(node, []):
                if edge.target not in parents:
                    parents[edge.target] = node
                    queue.append(edge.target)

        return None

    # ---------------------------------------------------------------------- #
    # Health
    # ---------------------------------------------------------------------- #

    def orphans(self, edge_types: Optional[List[str]] = None) -> List[str]:
        """Documents with zero inbound edges of the specified types.

        Args:
            edge_types: Restrict check to these edge types (default: explicit only).

        Returns:
            Sorted list of orphan doc_ids.
        """
        if edge_types is None:
            edge_types = ["explicit"]

        result = []
        for doc_id in self._nodes:
            inbound = self._in.get(doc_id, [])
            qualifying = [e for e in inbound if e.type in edge_types]
            if not qualifying:
                result.append(doc_id)

        result.sort()
        return result

    def hubs(
        self, top_k: int = 10, edge_types: Optional[List[str]] = None
    ) -> List[Tuple[str, int]]:
        """Documents ranked by inbound edge count (descending).

        Args:
            top_k: Maximum results to return.
            edge_types: Restrict count to these edge types (default: all types).

        Returns:
            List of ``(doc_id, inbound_count)`` tuples, descending.
        """
        scores: List[Tuple[str, int]] = []
        for doc_id in self._nodes:
            inbound = self._in.get(doc_id, [])
            if edge_types is not None:
                inbound = [e for e in inbound if e.type in edge_types]
            scores.append((doc_id, len(inbound)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    # ---------------------------------------------------------------------- #
    # PageRank
    # ---------------------------------------------------------------------- #

    def pagerank(
        self,
        damping: float = 0.85,
        max_iter: int = 100,
        tol: float = 1e-6,
    ) -> Dict[str, float]:
        """Iterative power-method PageRank over all nodes.

        Broken-link edges (``weight=0.0``) are excluded from the transition
        matrix. Semantic edge weights are used as transition weights (see ADR-017).

        Args:
            damping: Damping factor (default 0.85 per ADR-017 Decision 5).
            max_iter: Maximum iterations before returning unconverged result.
            tol: L∞ convergence tolerance (max absolute per-node delta).

        Returns:
            ``{doc_id: pagerank_score}`` — scores sum to 1.0.
        """
        n = len(self._nodes)
        if n == 0:
            return {}

        doc_ids = list(self._nodes.keys())
        idx = {d: i for i, d in enumerate(doc_ids)}

        # Initialise uniform distribution
        scores = [1.0 / n] * n

        # Precompute: for each node, its outbound edges with positive weight
        out_weighted: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
        for source, edges in self._out.items():
            si = idx[source]
            for edge in edges:
                if edge.weight > 0.0 and edge.target in idx:
                    out_weighted[si].append((idx[edge.target], edge.weight))

        # Outbound weight sums for normalisation
        out_totals = [sum(w for _, w in out_weighted[i]) for i in range(n)]

        for _ in range(max_iter):
            new_scores = [(1.0 - damping) / n] * n

            for si in range(n):
                total = out_totals[si]
                if total == 0.0:
                    # Dangling node: distribute its score uniformly
                    contribution = damping * scores[si] / n
                    for ti in range(n):
                        new_scores[ti] += contribution
                else:
                    for ti, w in out_weighted[si]:
                        new_scores[ti] += damping * scores[si] * (w / total)

            # L∞ convergence check
            delta = max(abs(new_scores[i] - scores[i]) for i in range(n))
            scores = new_scores
            if delta < tol:
                break

        return {doc_ids[i]: scores[i] for i in range(n)}

    # ---------------------------------------------------------------------- #
    # Serialisation helpers (used by GraphStore)
    # ---------------------------------------------------------------------- #

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the graph to a JSON-compatible dict."""
        edges_list = []
        for edges in self._out.values():
            for edge in edges:
                edges_list.append(edge.to_dict())

        return {
            "nodes": {doc_id: props.to_dict() for doc_id, props in self._nodes.items()},
            "edges": edges_list,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "KnowledgeGraph":
        """Deserialise from a JSON-compatible dict (produced by :meth:`to_dict`)."""
        g = cls()
        for doc_id, props_dict in d.get("nodes", {}).items():
            props = NodeProps.from_dict(props_dict)
            g._nodes[doc_id] = props
            g._out.setdefault(doc_id, [])
            g._in.setdefault(doc_id, [])

        for edge_dict in d.get("edges", []):
            edge = Edge.from_dict(edge_dict)
            # Ensure endpoint stubs exist
            for ep in (edge.source, edge.target):
                if ep not in g._nodes:
                    g._nodes[ep] = NodeProps()
                    g._out.setdefault(ep, [])
                    g._in.setdefault(ep, [])
            g._out[edge.source].append(edge)
            g._in[edge.target].append(edge)

        return g
