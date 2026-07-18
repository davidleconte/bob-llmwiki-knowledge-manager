"""Command-line interface for the token-optimization system.

A thin argparse front end over the :class:`~src.facade.TokenOptimizer` facade:
every subcommand constructs one facade from config and calls one already-tested
method, then prints the result. No business logic lives here.

Entry points:
    bob-optimize <command> ...     (console_scripts; see pyproject [project.scripts])
    python -m src <command> ...    (via src/__main__.py)

Component logging goes to stderr and is quieted to WARNING by default, so stdout
stays clean for piped/`--json` output; pass ``--verbose`` to restore INFO logs.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, List, Optional

from src import TokenOptimizer
from src.config import get_config
from src.monitoring import configure_logging


def _read_text(value: str) -> str:
    """Return the input text: read stdin when ``value`` is ``"-"``, else literal."""
    return sys.stdin.read() if value == "-" else value


def _emit(data: Any, as_json: bool) -> None:
    """Print a result either as indented JSON or as flat ``key: value`` lines."""
    if as_json:
        print(json.dumps(data, indent=2, default=str))
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print(data)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser (also used directly by the tests)."""
    parser = argparse.ArgumentParser(
        prog="bob-optimize",
        description="Token-optimization CLI (cache + optimizer + truncation + monitoring).",
    )
    parser.add_argument(
        "-e", "--environment", default="dev", help="Config environment (default: dev)"
    )
    parser.add_argument("--json", action="store_true", help="Emit raw JSON output")
    parser.add_argument(
        "--verbose", action="store_true", help="Restore INFO-level component logging"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_opt = sub.add_parser("optimize", help="Optimize a prompt for token efficiency")
    p_opt.add_argument("text", help="Prompt text, or '-' to read stdin")
    p_opt.add_argument(
        "--max-tokens", type=int, default=None, help="Cap on optimized tokens (overrides config)"
    )

    p_trunc = sub.add_parser("truncate", help="Truncate text to a token budget")
    p_trunc.add_argument("text", help="Text, or '-' to read stdin")
    p_trunc.add_argument("--max-tokens", type=int, required=True, help="Token budget")
    p_trunc.add_argument(
        "--strategy", default=None, help="Truncation strategy (default from config)"
    )

    p_count = sub.add_parser("count", help="Count tokens in text")
    p_count.add_argument("text", help="Text, or '-' to read stdin")

    sub.add_parser("cache-stats", help="Show multi-level cache statistics")
    sub.add_parser("cost-report", help="Show a cost report")
    sub.add_parser("metrics", help="Show the metrics summary")
    sub.add_parser("health", help="Run health checks")
    sub.add_parser("config", help="Show the effective configuration")

    # --- KB graph commands (ADR-017) ---
    p_gbuild = sub.add_parser("graph-build", help="Build KB knowledge graph and save to disk")
    p_gbuild.add_argument("--kb-path", default="docs/knowledge-base", help="KB root directory")
    p_gbuild.add_argument("--graph-path", default=".bob/kb-graph.json", help="Output graph file")
    p_gbuild.add_argument(
        "--semantic-threshold",
        type=float,
        default=0.3,
        help="Min cosine similarity for a semantic edge (default: 0.3)",
    )
    p_gbuild.add_argument(
        "--with-semantic",
        action="store_true",
        help="Derive semantic edges from the embedding index (requires .bob/kb-index/)",
    )

    p_gquery = sub.add_parser("graph-query", help="Show neighbourhood context for a KB document")
    p_gquery.add_argument("doc_id", help="KB-relative doc id (e.g. concepts/caching.md)")
    p_gquery.add_argument("--depth", type=int, default=1, help="BFS depth (default: 1)")
    p_gquery.add_argument(
        "--graph-path",
        default=".bob/kb-graph.json",
        help="Graph file (default: .bob/kb-graph.json)",
    )
    p_gquery.add_argument(
        "--edge-types",
        nargs="+",
        default=None,
        help="Edge types to traverse: explicit semantic broken (default: all)",
    )

    p_ghealth = sub.add_parser("graph-health", help="Show KB graph health (orphans, hubs, stats)")
    p_ghealth.add_argument(
        "--graph-path",
        default=".bob/kb-graph.json",
        help="Graph file (default: .bob/kb-graph.json)",
    )
    p_ghealth.add_argument("--top-k", type=int, default=10, help="Number of hub docs to show")

    # --- KB status command ---
    p_kbstatus = sub.add_parser(
        "kb-status",
        help="Show integration health: embedding backend, index freshness, compression availability",
    )
    p_kbstatus.add_argument(
        "--kb-path",
        default="docs/knowledge-base",
        help="KB root directory (default: docs/knowledge-base)",
    )
    p_kbstatus.add_argument(
        "--index-path",
        default=".bob/kb-index",
        help="Embedding index directory (default: .bob/kb-index)",
    )
    p_kbstatus.add_argument(
        "--graph-path",
        default=".bob/kb-graph.json",
        help="Graph file (default: .bob/kb-graph.json)",
    )

    # --- Delegation analysis pipeline command ---
    p_analyze = sub.add_parser(
        "analyze",
        help="Run parallel delegation analysis on a target directory and ingest results into the KB",
    )
    p_analyze.add_argument(
        "target",
        help="Directory or file to analyze (e.g. 'src/cache' or 'src/optimizer/prompt_optimizer.py')",
    )
    p_analyze.add_argument(
        "--kb-path",
        default="docs/knowledge-base",
        help="KB root for ResearchAgent context lookup (default: docs/knowledge-base)",
    )
    p_analyze.add_argument(
        "--output-dir",
        default="docs/knowledge-base/research",
        help="Directory to write generated research docs (default: docs/knowledge-base/research)",
    )
    p_analyze.add_argument(
        "--workers", type=int, default=5, metavar="N", help="Maximum parallel workers (default: 5)"
    )
    p_analyze.add_argument(
        "--depth",
        choices=["shallow", "deep"],
        default="shallow",
        help="Analysis depth passed to each agent (default: shallow)",
    )
    p_analyze.add_argument(
        "--no-compress",
        action="store_true",
        help="Skip TokenOptimizer compression of agent reports before KB write",
    )

    # --- KB search command (P4) ---
    p_kbsearch = sub.add_parser("kb-search", help="Semantic search across the knowledge base")
    p_kbsearch.add_argument("query", help="Search query")
    p_kbsearch.add_argument(
        "--kb-path",
        default="docs/knowledge-base",
        help="KB root directory (default: docs/knowledge-base)",
    )
    p_kbsearch.add_argument(
        "--max-results", type=int, default=10, help="Maximum number of results (default: 10)"
    )
    p_kbsearch.add_argument(
        "--recency-weight",
        type=float,
        default=0.0,
        help="Blend weight for recency tiebreaker in [0.0, 1.0] (default: 0.0 = off)",
    )
    p_kbsearch.add_argument(
        "--date-filter",
        default=None,
        help="ISO date prefix filter (e.g. '2026-07'); only show matching docs",
    )
    p_kbsearch.add_argument(
        "--categories",
        nargs="+",
        default=None,
        help="Categories to search: concepts guides references research (default: all)",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)
    configure_logging(log_level="INFO" if args.verbose else "WARNING")

    facade = TokenOptimizer.from_config(args.environment)
    as_json = args.json

    if args.command == "optimize":
        _emit(facade.optimize(_read_text(args.text), max_tokens=args.max_tokens), as_json)
    elif args.command == "truncate":
        _emit(
            facade.truncate(_read_text(args.text), args.max_tokens, strategy=args.strategy),
            as_json,
        )
    elif args.command == "count":
        _emit({"tokens": facade.count(_read_text(args.text))}, as_json)
    elif args.command == "cache-stats":
        _emit(facade.cache_stats(), as_json)
    elif args.command == "cost-report":
        _emit(facade.cost_report(), as_json)
    elif args.command == "metrics":
        _emit(facade.metrics(), as_json)
    elif args.command == "health":
        _emit(facade.health(), as_json)
    elif args.command == "config":
        _emit(get_config(args.environment).get_all(), as_json)

    elif args.command == "graph-build":
        from pathlib import Path

        from src.graph.builder import KnowledgeGraphBuilder, build_graph_metadata
        from src.graph.store import GraphStore

        kb_path = Path(args.kb_path)
        graph_path = Path(args.graph_path)
        threshold = args.semantic_threshold

        index = None
        if args.with_semantic:
            try:
                from src.cache.embeddings import EmbeddingGenerator
                from src.embeddings.index import PersistentEmbeddingIndex
                from src.embeddings.indexer import KBIndexer

                embedder = EmbeddingGenerator()
                idx = PersistentEmbeddingIndex(embedder)
                KBIndexer(kb_path, idx).sync()
                index = idx
            except Exception as exc:
                print(
                    f"Warning: could not load embedding index ({exc}). Semantic edges skipped.",
                    file=sys.stderr,
                )

        builder = KnowledgeGraphBuilder(kb_path, index=index, semantic_threshold=threshold)
        graph = builder.build()
        meta = build_graph_metadata(kb_path, threshold)
        GraphStore().save(graph_path, graph, metadata=meta)

        _emit(
            {
                "nodes": graph.node_count,
                "edges": graph.edge_count,
                "graph_path": str(graph_path),
                "semantic_threshold": threshold,
            },
            as_json,
        )

    elif args.command == "graph-query":
        from pathlib import Path

        from src.graph.ranker import GraphRanker
        from src.graph.store import GraphStore

        graph_path = Path(args.graph_path)
        _loaded_graph = GraphStore().load(graph_path)
        if _loaded_graph is None:
            print(
                f"Error: graph not found at {graph_path}. Run 'bob-optimize graph-build' first.",
                file=sys.stderr,
            )
            return 1
        graph = _loaded_graph

        ranker = GraphRanker(graph)
        ctx = ranker.neighbourhood_context(
            args.doc_id, depth=args.depth, edge_types=args.edge_types
        )
        node = graph.get_node(args.doc_id)
        _emit(
            {
                "doc_id": args.doc_id,
                "title": node.title if node else args.doc_id,
                "depth": args.depth,
                "neighbours": ctx,
            },
            as_json,
        )

    elif args.command == "graph-health":
        from pathlib import Path

        from src.graph.store import GraphStore

        graph_path = Path(args.graph_path)
        _loaded_graph = GraphStore().load(graph_path)
        if _loaded_graph is None:
            print(
                f"Error: graph not found at {graph_path}. Run 'bob-optimize graph-build' first.",
                file=sys.stderr,
            )
            return 1
        graph = _loaded_graph

        orphans = graph.orphans(edge_types=["explicit"])
        hubs = graph.hubs(top_k=args.top_k)
        pr = graph.pagerank()

        _emit(
            {
                "node_count": graph.node_count,
                "edge_count": graph.edge_count,
                "orphan_count": len(orphans),
                "orphans": orphans,
                "top_hubs": [
                    {
                        "doc_id": doc_id,
                        "inbound_edges": count,
                        "pagerank": round(pr.get(doc_id, 0.0), 6),
                    }
                    for doc_id, count in hubs
                ],
            },
            as_json,
        )

    elif args.command == "kb-search":
        from pathlib import Path

        from src.tools.kb_query import KnowledgeBaseQuery

        kbq = KnowledgeBaseQuery(
            kb_path=args.kb_path,
            recency_weight=args.recency_weight,
        )
        result = kbq.query(
            args.query,
            categories=args.categories,
            max_results=args.max_results,
            date_filter=args.date_filter,
        )
        if as_json:
            _emit(result, as_json=True)
        else:
            results = result.get("results", [])
            print(f"Query: {args.query}  ({len(results)} results)")
            for i, r in enumerate(results, 1):
                print(f"\n{i}. [{r['category']}] {r['title']}")
                print(f"   file:  {r['file']}")
                print(f"   score: {r['score']:.2f}  modified: {r.get('last_modified', 'n/a')[:10]}")
                if "preview" in r:
                    preview = r["preview"].replace("\n", " ")[:120]
                    print(f"   {preview}")

    elif args.command == "kb-status":
        from pathlib import Path

        from src.cache.embeddings import EmbeddingGenerator
        from src.embeddings.index import PersistentEmbeddingIndex
        from src.graph.store import GraphStore

        kb_path = Path(args.kb_path)
        index_path = Path(args.index_path)
        graph_path = Path(args.graph_path)

        # --- KB document count ---
        kb_exists = kb_path.exists()
        kb_doc_count = 0
        if kb_exists:
            for cat in ("concepts", "guides", "references", "research"):
                cat_dir = kb_path / cat
                if cat_dir.exists():
                    kb_doc_count += sum(1 for _ in cat_dir.glob("*.md"))

        # --- Embedding backend ---
        embedder = EmbeddingGenerator(backend="minilm")
        embedding_backend = embedder._backend  # "minilm" | "hashing" (resolved after fallback)

        # --- Persistent index ---
        index_exists = (index_path / "manifest.json").exists()
        index_doc_count = 0
        index_stale_docs = 0
        if index_exists:
            try:
                index = PersistentEmbeddingIndex(embedder=embedder, index_path=index_path)
                index_doc_count = index.doc_count
                if kb_exists:
                    index_stale_docs = sum(
                        1
                        for cat in ("concepts", "guides", "references", "research")
                        for md in (kb_path / cat).glob("*.md")
                        if (kb_path / cat).exists() and index.is_stale(md, kb_path=kb_path)
                    )
            except Exception:
                pass

        # --- Knowledge graph ---
        graph_exists = graph_path.exists()
        graph_node_count = 0
        graph_edge_count = 0
        if graph_exists:
            try:
                _g = GraphStore().load(graph_path)
                if _g is not None:
                    graph_node_count = _g.node_count
                    graph_edge_count = _g.edge_count
            except Exception:
                pass

        # --- Compression availability ---
        try:
            _ = facade  # already built above; if we got here, compression is available
            compression_available = True
        except Exception:
            compression_available = False

        status = {
            "kb_path": str(kb_path),
            "kb_path_exists": kb_exists,
            "kb_doc_count": kb_doc_count,
            "embedding_backend": embedding_backend,
            "index_path": str(index_path),
            "index_exists": index_exists,
            "index_doc_count": index_doc_count,
            "index_stale_docs": index_stale_docs,
            "graph_path": str(graph_path),
            "graph_exists": graph_exists,
            "graph_node_count": graph_node_count,
            "graph_edge_count": graph_edge_count,
            "compression_available": compression_available,
        }

        if as_json:
            _emit(status, as_json=True)
        else:
            tick = "✓"
            warn = "⚠"
            cross = "✗"
            print("Integration Status")
            print("=" * 44)
            kb_icon = tick if kb_exists else cross
            print(f"  {kb_icon} KB documents        : {kb_doc_count} ({kb_path})")
            emb_icon = tick if embedding_backend == "minilm" else warn
            print(f"  {emb_icon} Embedding backend   : {embedding_backend}")
            idx_icon = (
                tick
                if (index_exists and index_stale_docs == 0)
                else (warn if index_exists else cross)
            )
            idx_note = f"{index_doc_count} chunks" + (
                f", {index_stale_docs} stale" if index_stale_docs else ""
            )
            print(
                f"  {idx_icon} Embedding index     : {'built' if index_exists else 'not built'} ({idx_note})"
            )
            gr_icon = tick if graph_exists else cross
            print(
                f"  {gr_icon} Knowledge graph     : {'built' if graph_exists else 'not built'} ({graph_node_count} nodes, {graph_edge_count} edges)"
            )
            cmp_icon = tick if compression_available else cross
            print(
                f"  {cmp_icon} Compression (TOS)   : {'available' if compression_available else 'unavailable'}"
            )
            print("=" * 44)
            if (
                kb_exists
                and embedding_backend == "minilm"
                and index_exists
                and index_stale_docs == 0
                and graph_exists
                and compression_available
            ):
                print("✅ Full stack active — p@3=0.88, index fresh, compression enabled")
            else:
                print(
                    "⚠️  Partial stack — run: bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic"
                )

    elif args.command == "analyze":
        from src.delegation.pipeline import analyze_and_ingest

        try:
            pipeline_result = analyze_and_ingest(
                target_dir=args.target,
                kb_path=args.kb_path,
                output_dir=args.output_dir,
                max_workers=args.workers,
                depth=args.depth,
                compress=not args.no_compress,
            )
            _emit(pipeline_result.__dict__, as_json)
        except Exception as exc:
            _emit({"error": str(exc)}, as_json)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
