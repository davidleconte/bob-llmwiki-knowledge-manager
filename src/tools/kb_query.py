#!/usr/bin/env python3
"""Knowledge Base Query Utility.

Semantic search across knowledge base documents.

Scoring is keyword-based by default.  Pass an optional
:class:`~src.cache.embeddings.EmbeddingGenerator` to blend in cosine-similarity
scores via the ``embedding_weight`` parameter (0.0 = keyword only; 1.0 = embedding
only; values in between blend both scorers).

The embedding path is **opt-in** and defaults to pure keyword scoring
(``embedding_weight=0.0``) so existing callers are unaffected.  Before raising
the weight above 0, run an A/B validation test per ADR-014 to confirm that
embedding scores improve ``precision@3`` for your KB corpus.

See ADR-014 (``docs/adr/014-kb-query-embedding-scorer.md``) for the design
rationale, quality trade-offs, and the ``use_cache=False`` memory-safety
requirement.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from src.tools.safe_paths import resolve_within

if TYPE_CHECKING:
    from src.cache.embeddings import EmbeddingGenerator
    from src.embeddings.index import PersistentEmbeddingIndex


class KnowledgeBaseQuery:
    """Query knowledge base with keyword and optional embedding scoring.

    Three-tier fallback chain (ADR-014, ADR-015)::

        PersistentEmbeddingIndex   →  EmbeddingGenerator (P1-1)  →  keyword scorer
            (fastest, persists)          (per-query, accurate)       (original)

    Pass *index* for the P2 persistent path.  Pass *embedder* + *embedding_weight*
    for the P1 per-query path.  Leave both ``None`` for pure keyword scoring.

    Args:
        kb_path: Path to the knowledge base root directory.
        embedder: Optional :class:`~src.cache.embeddings.EmbeddingGenerator`
            instance.  When ``None`` (default) the scorer is keyword-only.
        embedding_weight: Blend weight for the embedding scorer in the range
            [0.0, 1.0].  ``0.0`` (default) means keyword-only; ``1.0`` means
            embedding-only.  Has no effect when *embedder* is ``None``.
        index: Optional :class:`~src.embeddings.index.PersistentEmbeddingIndex`.
            When provided, ``query()`` calls ``index.search()`` for the ranking
            pass instead of per-document embedding computation, then re-ranks
            the top-k candidates using the keyword scorer as a tie-breaker.
            Falls back to the embedder/keyword path if the index is empty.
    """

    def __init__(
        self,
        kb_path: str = "docs/knowledge-base",
        *,
        embedder: Optional["EmbeddingGenerator"] = None,
        embedding_weight: float = 0.0,
        index: Optional["PersistentEmbeddingIndex"] = None,
    ):
        self.kb_path = Path(kb_path)
        if not self.kb_path.exists():
            raise ValueError(f"Knowledge base not found: {kb_path}")

        self.categories = ["concepts", "guides", "references", "research"]

        if embedding_weight < 0.0 or embedding_weight > 1.0:
            raise ValueError(
                f"embedding_weight must be in [0.0, 1.0], got {embedding_weight}"
            )
        self._embedder = embedder
        self._embedding_weight = embedding_weight
        self._index = index  # PersistentEmbeddingIndex | None (P2-2)

    def query(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        max_results: int = 10,
        include_content: bool = False,
    ) -> Dict:
        """Query the knowledge base.

        When a :class:`~src.embeddings.index.PersistentEmbeddingIndex` was
        injected at construction, the query is answered by:

        1. ``index.search(query, top_k=max_results * 3)`` — fast semantic lookup
        2. Load each returned document and apply the keyword scorer as a
           tie-breaker (blended at ``embedding_weight``).
        3. Fall back silently to the full scan if the index returns nothing
           (empty or not yet built).

        Args:
            query: Search query
            categories: Categories to search (``None`` = all)
            max_results: Maximum number of results
            include_content: Include full content in results

        Returns:
            Dictionary with search results
        """
        if categories is None:
            categories = self.categories

        # Validate categories
        invalid = [c for c in categories if c not in self.categories]
        if invalid:
            return {"error": f"Invalid categories: {invalid}"}

        # --- P2 fast path: persistent index available ---
        if self._index is not None and self._index.doc_count > 0:
            return self._query_via_index(query, categories, max_results, include_content)

        return self._query_full_scan(query, categories, max_results, include_content)

    def _query_full_scan(
        self,
        query: str,
        categories: List[str],
        max_results: int,
        include_content: bool,
    ) -> Dict:
        """Full filesystem scan — keyword (+ optional P1 embedding) scoring."""
        all_results = []

        for category in categories:
            category_path = self.kb_path / category
            if not category_path.exists():
                continue

            for md_file in category_path.glob("*.md"):
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    score = self._calculate_relevance(query, content, md_file.name)

                    if score > 0:
                        result = {
                            "file": str(md_file.relative_to(self.kb_path)),
                            "category": category,
                            "title": self._extract_title(content),
                            "score": score,
                            "matches": self._find_matches(query, content),
                            "last_modified": datetime.fromtimestamp(
                                md_file.stat().st_mtime
                            ).isoformat(),
                        }
                        if include_content:
                            result["content"] = content
                        else:
                            result["preview"] = self._generate_preview(content, query)
                        all_results.append(result)

                except Exception:
                    continue

        all_results.sort(key=lambda x: x["score"], reverse=True)
        return {
            "query": query,
            "categories_searched": categories,
            "total_results": len(all_results),
            "results": all_results[:max_results],
        }

    def _query_via_index(
        self,
        query: str,
        categories: List[str],
        max_results: int,
        include_content: bool,
    ) -> Dict:
        """P2 fast path: rank via PersistentEmbeddingIndex, load matching files.

        Uses ``index.search()`` for ordering, then loads the actual files to
        populate the result dicts.  Only returns documents whose category is in
        *categories*.  Falls back to the full scan if no matching docs are found.
        """
        assert self._index is not None  # caller guarantees this
        # Fetch more candidates than needed to account for category filtering
        candidates = self._index.search(query, top_k=max_results * 4)

        all_results = []
        for doc_id, embed_score in candidates:
            # doc_id is a KB-relative path like "concepts/foo.md"
            parts = doc_id.split("/", 1)
            if len(parts) != 2:
                continue
            category, filename = parts[0], parts[1]
            if category not in categories:
                continue

            md_file = self.kb_path / doc_id
            if not md_file.exists():
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            # Keyword score as tie-breaker (blended at _embedding_weight)
            kw_score = self._keyword_score(query, content, filename)
            w = self._embedding_weight
            blended = (1.0 - w) * kw_score + w * embed_score * 15.0

            result: Dict = {
                "file": doc_id,
                "category": category,
                "title": self._extract_title(content),
                "score": blended,
                "matches": self._find_matches(query, content),
                "last_modified": datetime.fromtimestamp(
                    md_file.stat().st_mtime
                ).isoformat(),
            }
            if include_content:
                result["content"] = content
            else:
                result["preview"] = self._generate_preview(content, query)
            all_results.append(result)

            if len(all_results) >= max_results:
                break

        # If index returned nothing useful, fall back to full scan
        if not all_results:
            return self._query_full_scan(query, categories, max_results, include_content)

        all_results.sort(key=lambda x: x["score"], reverse=True)
        return {
            "query": query,
            "categories_searched": categories,
            "total_results": len(all_results),
            "results": all_results[:max_results],
        }

    def _calculate_relevance(self, query: str, content: str, filename: str) -> float:
        """Calculate relevance score for a document.

        When *embedding_weight* is 0.0 or no embedder is configured, the score
        is purely keyword-based (existing behaviour — no new imports touched).

        When an embedder is provided and *embedding_weight* > 0, the embedding
        cosine-similarity score is rescaled to the same [0, ~15] range as the
        keyword scorer and linearly blended:

            score = (1 - w) * keyword_score + w * embed_score

        Document embeddings are generated with ``use_cache=False`` to prevent
        the :attr:`~src.cache.embeddings.EmbeddingGenerator.embeddings_cache`
        dict from growing unboundedly (full document text as keys).  See ADR-014.
        """
        keyword_score = self._keyword_score(query, content, filename)

        if self._embedder is None or self._embedding_weight == 0.0:
            return keyword_score

        # Import lazily — only when the embedding path is actually used.
        from src.cache.embeddings import cosine_similarity_vectors

        q_vec = self._embedder.generate(query, use_cache=True)
        # use_cache=False: document content is large and unique; caching it
        # would grow embeddings_cache without bound (AF-5 / ADR-014).
        c_vec = self._embedder.generate(content[:2000], use_cache=False)
        # Rescale cosine similarity [0, 1] → [0, 15] to match keyword range.
        embed_score = cosine_similarity_vectors(q_vec, c_vec) * 15.0

        return (1.0 - self._embedding_weight) * keyword_score + self._embedding_weight * embed_score

    def _keyword_score(self, query: str, content: str, filename: str) -> float:
        """Pure keyword relevance score (original algorithm, unchanged)."""
        score = 0.0
        query_lower = query.lower()
        content_lower = content.lower()

        # Exact phrase match in title (highest weight)
        title = self._extract_title(content).lower()
        if query_lower in title:
            score += 10.0

        # Exact phrase match in filename
        if query_lower in filename.lower():
            score += 5.0

        # Word matches in content
        query_words = query_lower.split()
        for word in query_words:
            if len(word) < 3:  # Skip short words
                continue

            # Count occurrences
            count = content_lower.count(word)

            # Weight by position (earlier = more relevant)
            first_pos = content_lower.find(word)
            if first_pos >= 0:
                position_weight = 1.0 - (first_pos / len(content_lower))
                score += count * 0.5 * (1 + position_weight)

        # Bonus for multiple query words appearing together
        if len(query_words) > 1:
            for i in range(len(query_words) - 1):
                phrase = f"{query_words[i]} {query_words[i + 1]}"
                if phrase in content_lower:
                    score += 2.0

        # Bonus for matches in headings
        headings = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        for heading in headings:
            if query_lower in heading.lower():
                score += 3.0

        return score

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()

        return "Untitled"

    def _find_matches(self, query: str, content: str) -> List[Dict]:
        """Find matching lines in content"""
        matches = []
        lines = content.split("\n")
        query_lower = query.lower()

        for line_num, line in enumerate(lines, 1):
            if query_lower in line.lower():
                matches.append(
                    {
                        "line": line_num,
                        "text": line.strip()[:200],  # Truncate long lines
                    }
                )

                if len(matches) >= 5:  # Limit matches per file
                    break

        return matches

    def _generate_preview(self, content: str, query: str) -> str:
        """Generate preview snippet around query match"""
        lines = content.split("\n")
        query_lower = query.lower()

        # Find first match
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # Get context (2 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)

                preview_lines = lines[start:end]
                preview = "\n".join(preview_lines)

                # Truncate if too long
                if len(preview) > 500:
                    preview = preview[:500] + "..."

                return preview

        # No match found, return first few lines
        return "\n".join(lines[:5])

    def list_documents(self, category: Optional[str] = None) -> Dict:
        """List all documents in knowledge base"""
        if category and category not in self.categories:
            return {"error": f"Invalid category: {category}"}

        categories_to_list = [category] if category else self.categories
        documents = {}

        for cat in categories_to_list:
            cat_path = self.kb_path / cat
            if not cat_path.exists():
                continue

            md_files = list(cat_path.glob("*.md"))

            docs = []
            for md_file in md_files:
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    docs.append(
                        {
                            "file": md_file.name,
                            "title": self._extract_title(content),
                            "size_bytes": len(content),
                            "line_count": content.count("\n") + 1,
                            "last_modified": datetime.fromtimestamp(
                                md_file.stat().st_mtime
                            ).isoformat(),
                        }
                    )
                except Exception:
                    continue

            documents[cat] = docs

        return {
            "categories": categories_to_list,
            "total_documents": sum(len(docs) for docs in documents.values()),
            "documents": documents,
        }

    def get_cross_references(self, file_path: str) -> Dict:
        """Get cross-references for a document"""
        try:
            full_path = resolve_within(self.kb_path, file_path)
        except ValueError:
            return {"error": f"Invalid file path (escapes knowledge base): {file_path}"}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except Exception as e:
            return {"error": str(e)}

        # Find markdown links
        links = re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content)

        # Find references to other KB documents
        kb_refs = []
        external_refs = []

        for link_text, link_url in links:
            if link_url.startswith("http"):
                external_refs.append({"text": link_text, "url": link_url})
            elif link_url.endswith(".md"):
                kb_refs.append({"text": link_text, "file": link_url})

        # Find documents that reference this one
        referenced_by = []
        file_name = Path(file_path).name

        for category in self.categories:
            cat_path = self.kb_path / category
            if not cat_path.exists():
                continue

            for md_file in cat_path.glob("*.md"):
                if md_file.resolve() == full_path:  # full_path is resolved; match self
                    continue

                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        other_content = f.read()

                    if file_name in other_content or file_path in other_content:
                        referenced_by.append(
                            {
                                "file": str(md_file.relative_to(self.kb_path)),
                                "title": self._extract_title(other_content),
                            }
                        )
                except Exception:
                    continue

        return {
            "file": file_path,
            "title": self._extract_title(content),
            "kb_references": kb_refs,
            "external_references": external_refs,
            "referenced_by": referenced_by,
        }

    def get_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        stats = {"categories": {}, "total_documents": 0, "total_size_bytes": 0, "total_lines": 0}

        for category in self.categories:
            cat_path = self.kb_path / category
            if not cat_path.exists():
                continue

            md_files = list(cat_path.glob("*.md"))

            cat_stats = {"document_count": len(md_files), "total_size": 0, "total_lines": 0}

            for md_file in md_files:
                try:
                    size = md_file.stat().st_size
                    with open(md_file, "r", encoding="utf-8") as f:
                        lines = f.read().count("\n") + 1

                    cat_stats["total_size"] += size
                    cat_stats["total_lines"] += lines
                except Exception:
                    continue

            stats["categories"][category] = cat_stats
            stats["total_documents"] += cat_stats["document_count"]
            stats["total_size_bytes"] += cat_stats["total_size"]
            stats["total_lines"] += cat_stats["total_lines"]

        return stats


def main():
    """CLI interface for knowledge base query"""
    import argparse

    parser = argparse.ArgumentParser(description="Knowledge Base Query Utility")
    parser.add_argument("--kb-path", default="docs/knowledge-base", help="Path to knowledge base")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Query command
    query_parser = subparsers.add_parser("query", help="Search knowledge base")
    query_parser.add_argument("query", help="Search query")
    query_parser.add_argument("--categories", nargs="+", help="Categories to search")
    query_parser.add_argument("--max-results", type=int, default=10, help="Maximum results")
    query_parser.add_argument("--include-content", action="store_true", help="Include full content")

    # List command
    list_parser = subparsers.add_parser("list", help="List documents")
    list_parser.add_argument("--category", help="Category to list")

    # Cross-references command
    xref_parser = subparsers.add_parser("xref", help="Get cross-references")
    xref_parser.add_argument("file", help="File path")

    # Stats command
    subparsers.add_parser("stats", help="Get statistics")

    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    try:
        kb = KnowledgeBaseQuery(args.kb_path)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    result = None

    if args.command == "query":
        result = kb.query(
            args.query,
            categories=args.categories,
            max_results=args.max_results,
            include_content=args.include_content,
        )
    elif args.command == "list":
        result = kb.list_documents(args.category)
    elif args.command == "xref":
        result = kb.get_cross_references(args.file)
    elif args.command == "stats":
        result = kb.get_statistics()
    else:
        parser.print_help()
        sys.exit(1)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        # Text output
        if args.command == "query":
            print(f"\n{'=' * 80}")
            print(f"Query: {result['query']}")
            print(f"Results: {result['total_results']}")
            print("=" * 80)

            for i, res in enumerate(result["results"], 1):
                print(f"\n{i}. {res['title']}")
                print(f"   File: {res['file']}")
                print(f"   Score: {res['score']:.2f}")
                print(f"   Category: {res['category']}")

                if res.get("matches"):
                    print("   Matches:")
                    for match in res["matches"][:3]:
                        print(f"     Line {match['line']}: {match['text'][:100]}")

        elif args.command == "list":
            print(f"\n{'=' * 80}")
            print("Knowledge Base Documents")
            print(f"Total: {result['total_documents']}")
            print("=" * 80)

            for category, docs in result["documents"].items():
                print(f"\n{category.upper()} ({len(docs)} documents):")
                for doc in docs:
                    print(f"  - {doc['title']}")
                    print(f"    {doc['file']} ({doc['line_count']} lines)")

        elif args.command == "xref":
            print(f"\n{'=' * 80}")
            if "error" in result:
                print(f"Error: {result['error']}")
                return
            print(f"Cross-References: {result['title']}")
            print("=" * 80)

            print(f"\nKB References ({len(result['kb_references'])}):")
            for ref in result["kb_references"]:
                print(f"  - {ref['text']} → {ref['file']}")

            print(f"\nExternal References ({len(result['external_references'])}):")
            for ref in result["external_references"][:10]:
                print(f"  - {ref['text']} → {ref['url']}")

            print(f"\nReferenced By ({len(result['referenced_by'])}):")
            for ref in result["referenced_by"]:
                print(f"  - {ref['title']} ({ref['file']})")

        elif args.command == "stats":
            print(f"\n{'=' * 80}")
            print("Knowledge Base Statistics")
            print("=" * 80)

            print(f"\nTotal Documents: {result['total_documents']}")
            print(f"Total Size: {result['total_size_bytes']:,} bytes")
            print(f"Total Lines: {result['total_lines']:,}")

            print("\nBy Category:")
            for category, stats in result["categories"].items():
                print(f"  {category}:")
                print(f"    Documents: {stats['document_count']}")
                print(f"    Size: {stats['total_size']:,} bytes")
                print(f"    Lines: {stats['total_lines']:,}")


if __name__ == "__main__":
    main()
