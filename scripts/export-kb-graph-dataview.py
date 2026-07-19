#!/usr/bin/env python3
"""
export-kb-graph-dataview.py — CLI wrapper for dataview_export.inject_dataview.

Usage:
    python3 scripts/export-kb-graph-dataview.py [--graph-path PATH] \
        [--export-path PATH] [--top-n N] [--min-weight W]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dataview_export import inject_dataview


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inject semantic_links frontmatter into exported KB documents."
    )
    parser.add_argument(
        "--graph-path",
        default=".bob/kb-graph.json",
        help="Path to kb-graph.json (default: .bob/kb-graph.json)",
    )
    parser.add_argument(
        "--export-path",
        default="kb-export/knowledge-base",
        help="Path to the exported KB directory (default: kb-export/knowledge-base)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=0,
        help="Max neighbours per document (0 = all above threshold, default: 0)",
    )
    parser.add_argument(
        "--min-weight",
        type=float,
        default=0.30,
        help="Minimum cosine weight to include a semantic edge (default: 0.30)",
    )
    args = parser.parse_args()

    graph_path = Path(args.graph_path)
    if not graph_path.exists():
        print(f"ERROR: graph file not found: {graph_path}", file=sys.stderr)
        sys.exit(1)

    with open(graph_path, encoding="utf-8") as fh:
        graph_dict = json.load(fh)

    stats = inject_dataview(
        export_path=args.export_path,
        graph_dict=graph_dict,
        top_n=args.top_n,
        min_weight=args.min_weight,
    )

    print("✅ Dataview injection complete")
    print(f"   files_annotated : {stats['files_annotated']}")
    print(f"   total_links     : {stats['total_links']}")
    print()

    # Sample Dataview query
    print("📋 Sample Dataview query (paste into an Obsidian note):")
    print()
    print("```dataview")
    print('TABLE semantic_links FROM "knowledge-base/concepts"')
    print("WHERE length(semantic_links) > 0")
    print("SORT file.name ASC")
    print("```")


if __name__ == "__main__":
    main()
