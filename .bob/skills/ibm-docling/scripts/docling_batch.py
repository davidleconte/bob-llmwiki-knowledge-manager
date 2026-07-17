#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
docling_batch.py — convert a whole directory (or glob) of documents in one pass,
reusing a single DocumentConverter (models load once), and write a manifest.

For each input it writes <stem>.<ext> into --outdir and records success/failure
in manifest.json so a downstream pipeline can retry only the failures.

Example:
  python3 docling_batch.py ./inbox --outdir ./out --to md --glob "*.pdf"

Exit codes: 0 all ok · 1 one or more documents failed · 2 missing dependency.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
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


def _export(doc, out_path: Path, to: str) -> None:
    if to == "md":
        out_path.write_text(doc.export_to_markdown(), encoding="utf-8")
    elif to == "text":
        out_path.write_text(doc.export_to_markdown(strict_text=True), encoding="utf-8")
    elif to == "json":
        out_path.write_text(
            json.dumps(doc.export_to_dict(), indent=2, default=str, ensure_ascii=False),
            encoding="utf-8",
        )
    elif to == "doctags":
        out_path.write_text(doc.export_to_doctags(), encoding="utf-8")
    else:  # pragma: no cover
        raise ValueError(f"unsupported --to for batch: {to}")


_EXT = {"md": "md", "text": "txt", "json": "json", "doctags": "doctags"}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="docling_batch.py", description="Batch-convert a directory of documents."
    )
    p.add_argument("indir", help="directory containing input documents")
    p.add_argument("--outdir", required=True, help="directory for converted output")
    p.add_argument("--glob", default="*", help='filename glob, e.g. "*.pdf" (default: all files)')
    p.add_argument("--to", choices=["md", "text", "json", "doctags"], default="md")
    p.add_argument("--no-ocr", action="store_true")
    p.add_argument("--recursive", action="store_true", help="recurse into subdirectories")
    args = p.parse_args(argv)

    if not _has("docling"):
        return _die("error: docling not installed. Run: pip install docling docling-core", 2)

    indir = Path(args.indir)
    if not indir.is_dir():
        return _die(f"error: not a directory: {indir}", 1)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    pattern = args.glob
    files = sorted(indir.rglob(pattern) if args.recursive else indir.glob(pattern))
    files = [f for f in files if f.is_file()]
    if not files:
        return _die(f"error: no files matched {pattern} in {indir}", 1)

    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    opts = PdfPipelineOptions()
    opts.do_ocr = not args.no_ocr
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )

    manifest = []
    failures = 0
    for f in files:
        started = time.time()
        out_path = outdir / f"{f.stem}.{_EXT[args.to]}"
        try:
            doc = converter.convert(str(f)).document
            _export(doc, out_path, args.to)
            manifest.append(
                {
                    "input": str(f),
                    "output": str(out_path),
                    "status": "ok",
                    "pages": len(getattr(doc, "pages", {}) or {}),
                    "seconds": round(time.time() - started, 2),
                }
            )
            sys.stderr.write(f"ok   {f.name} -> {out_path.name}\n")
        except Exception as e:  # noqa: BLE001
            failures += 1
            first = (str(e).splitlines() or [""])[0][:160]
            manifest.append(
                {"input": str(f), "status": "fail", "error": f"{type(e).__name__}: {first}"}
            )
            sys.stderr.write(f"FAIL {f.name}: {type(e).__name__}\n")

    manifest_path = outdir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    sys.stderr.write(
        f"\ndone: {len(files) - failures}/{len(files)} converted; manifest -> {manifest_path}\n"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
