"""GraphStore — atomic JSON persistence for :class:`~src.graph.graph.KnowledgeGraph`.

Mirrors the atomic write pattern of :class:`~src.embeddings.store.FileBackedVectorStore`
(write-to-temp-then-rename) so a crash mid-write leaves the previous version intact.

Design decisions: ADR-017 Decision 4.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from src.graph.graph import KnowledgeGraph

logger = logging.getLogger(__name__)

# Default location (ADR-017 Decision 4)
DEFAULT_GRAPH_PATH = Path(".bob/kb-graph.json")


class GraphStore:
    """Atomic read/write of :class:`~src.graph.graph.KnowledgeGraph` to JSON.

    Storage layout (ADR-017)::

        .bob/kb-graph.json   — single flat JSON file
            {
              "nodes": {doc_id: NodeProps dict, ...},
              "edges": [Edge dict, ...],
              "metadata": {...}
            }

    Writes are atomic: data goes to a temp file in the same directory then
    ``os.replace()`` (rename) so no partial file is ever visible.
    """

    def load(self, graph_path: Path) -> Optional[KnowledgeGraph]:
        """Load a :class:`~src.graph.graph.KnowledgeGraph` from *graph_path*.

        Returns ``None`` if the file does not exist or is corrupt.

        Args:
            graph_path: Path to the ``kb-graph.json`` file.

        Returns:
            Loaded :class:`~src.graph.graph.KnowledgeGraph` or ``None``.
        """
        if not graph_path.exists():
            return None

        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                raw: Dict[str, Any] = json.load(f)
        except Exception as exc:
            logger.warning("kb_graph_load_failed path=%s error=%s", graph_path, exc)
            return None

        try:
            graph = KnowledgeGraph.from_dict(raw)
        except Exception as exc:
            logger.warning("kb_graph_deserialise_failed path=%s error=%s", graph_path, exc)
            return None

        meta = raw.get("metadata", {})
        logger.debug(
            "kb_graph_loaded nodes=%d edges=%d",
            meta.get("node_count", graph.node_count),
            meta.get("edge_count", graph.edge_count),
        )
        return graph

    def save(
        self,
        graph_path: Path,
        graph: KnowledgeGraph,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Atomically write *graph* to *graph_path*.

        Creates parent directories if they do not exist.

        Args:
            graph_path: Target ``kb-graph.json`` path.
            graph: Graph to serialise.
            metadata: Optional dict stored under the ``"metadata"`` key
                (e.g. build timestamp, kb_path, semantic_threshold).

        Raises:
            OSError: If the directory cannot be created or the rename fails.
        """
        graph_path.parent.mkdir(parents=True, exist_ok=True)

        payload = graph.to_dict()
        payload["metadata"] = {
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
            **(metadata or {}),
        }

        # Atomic write: temp file in same directory → os.replace()
        fd, tmp_path = tempfile.mkstemp(
            dir=str(graph_path.parent), suffix=".json.tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            os.replace(tmp_path, str(graph_path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        logger.debug(
            "kb_graph_saved nodes=%d edges=%d path=%s",
            graph.node_count,
            graph.edge_count,
            graph_path,
        )

    def delete(self, graph_path: Path) -> None:
        """Remove *graph_path*. No-op if absent.

        Args:
            graph_path: Path to the ``kb-graph.json`` file.
        """
        if graph_path.exists():
            graph_path.unlink()
            logger.info("kb_graph_deleted path=%s", graph_path)
