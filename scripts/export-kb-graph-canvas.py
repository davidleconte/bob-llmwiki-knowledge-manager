#!/usr/bin/env python3
"""
export-kb-graph-canvas.py — CLI wrapper for canvas_export.build_canvas.

Usage:
    python scripts/export-kb-graph-canvas.py [--graph-path PATH] [--output-path PATH]

Defaults:
    --graph-path   .bob/kb-graph.json
    --output-path  kb-export/kb-semantic-graph.canvas
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from canvas_export import build_canvas

_DEFAULT_GRAPH  = ".bob/kb-graph.json"
_DEFAULT_OUTPUT = "kb-export/kb-semantic-graph.canvas"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export kb-graph.json as an Obsidian Canvas file."
    )
    parser.add_argument(
        "--graph-path",
        default=_DEFAULT_GRAPH,
        help=f"Path to kb-graph.json (default: {_DEFAULT_GRAPH})",
    )
    parser.add_argument(
        "--output-path",
        default=_DEFAULT_OUTPUT,
        help=f"Destination .canvas file (default: {_DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    graph_path  = Path(args.graph_path)
    output_path = Path(args.output_path)

    if not graph_path.exists():
        print(f"ERROR: graph file not found: {graph_path}", file=sys.stderr)
        sys.exit(1)

    with open(graph_path, encoding="utf-8") as fh:
        graph_dict = json.load(fh)

    canvas = build_canvas(graph_dict, output_path)

    # Summary
    raw_edges = graph_dict.get("edges", [])
    from collections import Counter
    type_counts = Counter(e.get("type", "unknown") for e in raw_edges)

    print(f"Canvas export complete: {output_path}")
    print(f"  nodes : {len(canvas['nodes'])}")
    print(f"  edges : {len(canvas['edges'])}")
    for etype, count in sorted(type_counts.items()):
        print(f"    {etype:<12} {count}")


if __name__ == "__main__":
    main()
