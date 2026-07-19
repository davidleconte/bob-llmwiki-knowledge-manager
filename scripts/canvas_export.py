"""
canvas_export.py — Build an Obsidian Canvas JSON from a kb-graph.json dict.

Public API
----------
build_canvas(graph_dict, output_path) -> dict

No src/ imports. stdlib only.
"""

import hashlib
import json
import os
from pathlib import Path

# Column x-positions for each category (pixels)
_CATEGORY_X = {
    "concepts":   0,
    "guides":     800,
    "references": 1600,
    "research":   2400,
}

# Node dimensions
_NODE_WIDTH  = 320
_NODE_HEIGHT = 60

# Vertical spacing inside a group and gap between groups
_VERT_SPACING = 140
_GROUP_GAP    = 120

# Obsidian edge colour codes
_EDGE_COLOR = {
    "explicit": "2",   # green
    "semantic": "4",   # blue
    "broken":   "1",   # red
}


def _node_id(doc_id: str) -> str:
    return hashlib.md5(doc_id.encode()).hexdigest()[:8]


def _edge_id(source: str, target: str, etype: str) -> str:
    return hashlib.md5((source + target + etype).encode()).hexdigest()[:8]


def _layout_nodes(nodes: dict) -> dict:
    """Return {doc_id: (x, y)} using deterministic sub-clustered grid layout."""
    # Bucket nodes by category then by first tag (alpha)
    buckets: dict[str, dict[str, list[str]]] = {cat: {} for cat in _CATEGORY_X}

    for doc_id, meta in nodes.items():
        cat = meta.get("category", "concepts")
        if cat not in buckets:
            cat = "concepts"
        tags = meta.get("tags") or []
        first_tag = tags[0] if tags else ""
        buckets[cat].setdefault(first_tag, []).append(doc_id)

    positions: dict[str, tuple[int, int]] = {}

    for cat, tag_groups in buckets.items():
        x = _CATEGORY_X[cat]
        y = 0
        # Sort groups alphabetically by tag name
        for tag in sorted(tag_groups):
            doc_ids = sorted(tag_groups[tag])  # alphabetical within group
            for doc_id in doc_ids:
                positions[doc_id] = (x, y)
                y += _VERT_SPACING
            y += _GROUP_GAP  # gap after each group

    return positions


def build_canvas(graph_dict: dict, output_path) -> dict:
    """Build Obsidian Canvas JSON from kb-graph.json dict.

    Writes the canvas atomically to output_path (write to .tmp then rename).
    Returns the canvas dict.

    Parameters
    ----------
    graph_dict : dict
        Parsed content of kb-graph.json — must have "nodes" and "edges" keys.
    output_path : str | Path
        Destination path for the .canvas file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    raw_nodes: dict = graph_dict.get("nodes", {})
    raw_edges: list = graph_dict.get("edges", [])

    # Build node positions
    positions = _layout_nodes(raw_nodes)

    # Build canvas nodes — only include nodes that appear in the graph
    canvas_nodes = []
    for doc_id, meta in raw_nodes.items():
        nid = _node_id(doc_id)
        x, y = positions.get(doc_id, (0, 0))
        canvas_nodes.append({
            "id":     nid,
            "type":   "file",
            "file":   f"knowledge-base/{doc_id}",
            "x":      x,
            "y":      y,
            "width":  _NODE_WIDTH,
            "height": _NODE_HEIGHT,
        })

    # Build canvas edges
    canvas_edges = []
    for edge in raw_edges:
        src  = edge.get("source", "")
        tgt  = edge.get("target", "")
        etype = edge.get("type", "semantic")
        weight = edge.get("weight")
        label = edge.get("label")

        # Determine label
        if etype == "semantic":
            edge_label = str(round(weight, 2)) if weight is not None else None
        else:
            edge_label = label  # may be None

        canvas_edge: dict = {
            "id":       _edge_id(src, tgt, etype),
            "fromNode": _node_id(src),
            "toNode":   _node_id(tgt),
            "color":    _EDGE_COLOR.get(etype, "4"),
        }
        if edge_label is not None:
            canvas_edge["label"] = edge_label

        canvas_edges.append(canvas_edge)

    canvas = {"nodes": canvas_nodes, "edges": canvas_edges}

    # Atomic write
    tmp_path = output_path.with_suffix(".canvas.tmp")
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(canvas, fh, ensure_ascii=False)
    os.replace(tmp_path, output_path)

    return canvas
