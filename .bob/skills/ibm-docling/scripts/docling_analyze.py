#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
docling_analyze.py — inspect the STRUCTURE of a document without dumping its full
content. Prints a compact report: page count, heading tree, table & figure
inventory (with captions and page numbers), and per-label item counts.

Accepts a source document (converts it) OR an existing DoclingDocument .json
(fast, no re-conversion). Also optionally dumps every table to CSV.

Use this to answer "what's in this document?", "show me the outline", "how many
tables are there and on which pages?" — cheaply and structurally.

Exit codes: 0 ok · 1 runtime/usage error · 2 missing dependency.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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
    p = Path(source)
    if p.suffix.lower() == ".json" and p.is_file():
        from docling_core.types.doc.document import DoclingDocument

        return DoclingDocument.model_validate(json.loads(p.read_text(encoding="utf-8")))
    from docling.document_converter import DocumentConverter

    return DocumentConverter().convert(source).document


def _label(item) -> str:
    lab = getattr(item, "label", None)
    return getattr(lab, "name", None) or getattr(lab, "value", None) or str(lab or "")


def _first_page(item) -> int | None:
    for prov in getattr(item, "prov", None) or []:
        p = getattr(prov, "page_no", None)
        if p is not None:
            return int(p)
    return None


def analyze(doc) -> dict:
    label_counts: Counter = Counter()
    outline: list[dict] = []
    pages: set[int] = set()

    for item, level in doc.iterate_items():
        lab = _label(item)
        label_counts[lab] += 1
        fp = _first_page(item)
        if fp is not None:
            pages.add(fp)
        text = getattr(item, "text", None)
        if lab in ("SECTION_HEADER", "TITLE") and text:
            outline.append({"level": level, "label": lab, "text": str(text).strip()[:120], "page": fp})

    tables = []
    for i, t in enumerate(getattr(doc, "tables", []) or []):
        cap = ""
        try:
            cap = t.caption_text(doc) or ""
        except Exception:  # noqa: BLE001
            pass
        nrows = getattr(getattr(t, "data", None), "num_rows", None)
        ncols = getattr(getattr(t, "data", None), "num_cols", None)
        tables.append({"index": i, "caption": cap[:100], "rows": nrows, "cols": ncols, "page": _first_page(t)})

    figures = []
    for i, pic in enumerate(getattr(doc, "pictures", []) or []):
        cap = ""
        try:
            cap = pic.caption_text(doc) or ""
        except Exception:  # noqa: BLE001
            pass
        figures.append({"index": i, "caption": cap[:100], "page": _first_page(pic)})

    return {
        "pages": len(getattr(doc, "pages", {}) or {}) or (max(pages) if pages else 0),
        "label_counts": dict(label_counts),
        "num_headings": len(outline),
        "num_tables": len(tables),
        "num_figures": len(figures),
        "outline": outline,
        "tables": tables,
        "figures": figures,
    }


def _print_human(report: dict) -> None:
    w = sys.stderr.write
    w(f"\nDocument structure — {report['pages']} page(s)\n")
    w(f"  headings: {report['num_headings']}  tables: {report['num_tables']}  figures: {report['num_figures']}\n")
    if report["outline"]:
        w("\nOutline:\n")
        for h in report["outline"][:60]:
            indent = "  " * max(h["level"], 1)
            pg = f"  (p.{h['page']})" if h["page"] is not None else ""
            w(f"{indent}{'#' * max(h['level'], 1)} {h['text']}{pg}\n")
    if report["tables"]:
        w("\nTables:\n")
        for t in report["tables"]:
            pg = f"p.{t['page']}" if t["page"] is not None else "?"
            dims = f"{t['rows']}x{t['cols']}" if t["rows"] else ""
            w(f"  [{t['index']}] {pg} {dims} {t['caption']}\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="docling_analyze.py", description="Report document structure (headings/tables/figures)."
    )
    p.add_argument("source", help="document path/URL, or an existing DoclingDocument .json")
    p.add_argument("-o", "--output", help="write JSON report to this file (also prints human summary to stderr)")
    p.add_argument("--tables-dir", help="also export every table as CSV into this directory")
    p.add_argument("--json-only", action="store_true", help="print JSON report to stdout, no human summary")
    args = p.parse_args(argv)

    if not _has("docling"):
        return _die("error: docling not installed. Run: pip install docling docling-core", 2)

    try:
        doc = _load_doc(args.source)
        report = analyze(doc)
    except Exception as e:  # noqa: BLE001
        first = (str(e).splitlines() or [""])[0][:200]
        return _die(f"error: analysis failed ({type(e).__name__}: {first})", 1)

    if args.tables_dir:
        outdir = Path(args.tables_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        n = 0
        for i, t in enumerate(getattr(doc, "tables", []) or []):
            try:
                df = t.export_to_dataframe(doc=doc)
            except TypeError:
                df = t.export_to_dataframe()
            df.to_csv(outdir / f"table_{i + 1}.csv", index=False)
            n += 1
        sys.stderr.write(f"note: wrote {n} table CSV(s) to {outdir}/\n")

    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        sys.stderr.write(f"note: wrote {args.output}\n")
    if args.json_only:
        sys.stdout.write(payload + "\n")
    elif not args.output:
        sys.stdout.write(payload + "\n")

    if not args.json_only:
        _print_human(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
