#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
docling_chunk.py — turn a document (or an existing DoclingDocument JSON) into
RAG-ready chunks and write them as JSONL, one embedding-ready record per line.

Each record:
  {
    "id": "<source>#<n>",
    "text": "<contextualized text (headings prepended)>",
    "raw_text": "<chunk text without heading context>",
    "headings": ["H1", "H2", ...],
    "page_numbers": [3, 4],
    "source": "<source path or url>",
    "token_count": 123
  }

`text` is what you embed; it is produced by chunker.contextualize() so each
chunk carries its section-heading breadcrumb — critical for retrieval quality.

Strategies:
  hybrid       (default) heading-aware split, then merge/split to a token budget
  hierarchical pure structure-based split (no tokenizer needed)

Tokenizers (hybrid only):
  hf     HuggingFace tokenizer (default: sentence-transformers/all-MiniLM-L6-v2)
  openai tiktoken for OpenAI embedding models (needs docling-core[chunking-openai])

Exit codes: 0 ok · 1 runtime/usage error · 2 missing dependency.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _has(module: str) -> bool:
    try:
        __import__(module)
        return True
    except ImportError:
        return False


def _die(msg: str, code: int) -> int:
    sys.stderr.write(msg if msg.endswith("\n") else msg + "\n")
    return code


def _load_doc(source: str):
    """Load a DoclingDocument from an existing JSON export, else convert the source."""
    p = Path(source)
    if p.suffix.lower() == ".json" and p.is_file():
        from docling_core.types.doc.document import DoclingDocument

        data = json.loads(p.read_text(encoding="utf-8"))
        return DoclingDocument.model_validate(data)

    from docling.document_converter import DocumentConverter

    return DocumentConverter().convert(source).document


def _make_chunker(args):
    if args.strategy == "hierarchical":
        from docling_core.transforms.chunker.hierarchical_chunker import (
            HierarchicalChunker,
        )

        return HierarchicalChunker()

    from docling.chunking import HybridChunker

    if args.tokenizer == "openai":
        import tiktoken
        from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer

        tok = OpenAITokenizer(
            tokenizer=tiktoken.encoding_for_model(args.openai_model),
            max_tokens=args.max_tokens,
        )
    else:
        from docling_core.transforms.chunker.tokenizer.huggingface import (
            HuggingFaceTokenizer,
        )

        tok = HuggingFaceTokenizer.from_pretrained(
            model_name=args.hf_model, max_tokens=args.max_tokens
        )
    return HybridChunker(tokenizer=tok, merge_peers=not args.no_merge_peers)


def _headings(meta) -> list[str]:
    h = getattr(meta, "headings", None)
    return list(h) if h else []


def _page_numbers(meta) -> list[int]:
    pages: set[int] = set()
    origin = getattr(meta, "origin", None)
    pno = getattr(origin, "page_no", None)
    if pno is not None:
        pages.add(int(pno))
    for item in getattr(meta, "doc_items", None) or []:
        for prov in getattr(item, "prov", None) or []:
            p = getattr(prov, "page_no", None)
            if p is not None:
                pages.add(int(p))
    return sorted(pages)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="docling_chunk.py",
        description="Chunk a document into RAG-ready JSONL records.",
    )
    p.add_argument("source", help="document path/URL, or an existing DoclingDocument .json")
    p.add_argument("-o", "--output", help="output .jsonl (stdout if omitted)")
    p.add_argument("--strategy", choices=["hybrid", "hierarchical"], default="hybrid")
    p.add_argument("--tokenizer", choices=["hf", "openai"], default="hf")
    p.add_argument("--hf-model", default="sentence-transformers/all-MiniLM-L6-v2")
    p.add_argument("--openai-model", default="text-embedding-3-small")
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--no-merge-peers", action="store_true", help="do not merge adjacent small chunks")
    args = p.parse_args(argv)

    if not _has("docling") or not _has("docling_core"):
        return _die("error: docling not installed. Run: pip install docling docling-core", 2)
    if args.tokenizer == "openai" and not _has("tiktoken"):
        return _die(
            "error: OpenAI tokenizer needs tiktoken. Run: pip install 'docling-core[chunking-openai]'",
            2,
        )

    try:
        doc = _load_doc(args.source)
        chunker = _make_chunker(args)
        chunks = list(chunker.chunk(dl_doc=doc))
    except Exception as e:  # noqa: BLE001
        first = (str(e).splitlines() or [""])[0][:200]
        return _die(f"error: chunking failed ({type(e).__name__}: {first})", 1)

    out_fh = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    token_counts: list[int] = []
    try:
        for i, chunk in enumerate(chunks):
            text = chunker.contextualize(chunk=chunk)
            try:
                n_tok = chunker.tokenizer.count_tokens(text)  # hybrid only
            except Exception:  # noqa: BLE001
                n_tok = len(text.split())
            token_counts.append(n_tok)
            record = {
                "id": f"{args.source}#{i}",
                "text": text,
                "raw_text": chunk.text,
                "headings": _headings(chunk.meta),
                "page_numbers": _page_numbers(chunk.meta),
                "source": args.source,
                "token_count": n_tok,
            }
            out_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    finally:
        if out_fh is not sys.stdout:
            out_fh.close()

    if token_counts:
        stats = {
            "chunks": len(token_counts),
            "tokens_min": min(token_counts),
            "tokens_max": max(token_counts),
            "tokens_avg": round(sum(token_counts) / len(token_counts), 1),
            "output": args.output or "<stdout>",
        }
    else:
        stats = {"chunks": 0, "output": args.output or "<stdout>"}
    sys.stderr.write("summary: " + json.dumps(stats) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
