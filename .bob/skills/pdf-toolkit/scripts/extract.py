#!/usr/bin/env python3
"""
extract.py — read / parse / extract content from PDFs (and other docs).

Tiered engine selection (auto by default):

  docling     High-fidelity layout, tables, figures, OCR, code/formula.
              Heavy (torch + models). Handles PDF/DOCX/XLSX/PPTX/HTML/images.
  pdfplumber  Fast, pure-python text + table extraction for digital PDFs.
              No OCR (scanned PDFs yield little/no text).

`--engine auto` uses docling if importable, else falls back to pdfplumber
and prints a note to stderr so the caller knows fidelity was reduced.

Output formats:  md (default) | text | json | tables (CSV per table)
Extras:          --images (docling only), --ocr (docling only)

Exit codes: 0 ok, 1 runtime error, 2 no usable engine installed.
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


# --------------------------------------------------------------------------- #
# docling engine (high fidelity)
# --------------------------------------------------------------------------- #
def extract_docling(args) -> int:
    # Silence docling's verbose per-page pipeline logging (it dumps whole page
    # dictionaries on parse failures); extract.py surfaces its own concise error.
    import logging
    logging.getLogger("docling").setLevel(logging.CRITICAL)

    from docling.datamodel.accelerator_options import (
        AcceleratorDevice,
        AcceleratorOptions,
    )
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import (
        PdfPipelineOptions,
        TableFormerMode,
    )
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.types.doc import ImageRefMode

    opts = PdfPipelineOptions()
    opts.do_ocr = bool(args.ocr)
    opts.do_table_structure = True
    opts.table_structure_options.mode = (
        TableFormerMode.ACCURATE if args.accurate_tables else TableFormerMode.FAST
    )
    opts.table_structure_options.do_cell_matching = True
    if args.ocr and args.lang:
        opts.ocr_options.lang = args.lang.split("+")  # e.g. "eng+fra" -> ["eng","fra"]
    if args.images or args.to == "images":
        opts.generate_picture_images = True
        opts.generate_page_images = True
        opts.images_scale = 2.0
    device = {
        "auto": AcceleratorDevice.AUTO,
        "cpu": AcceleratorDevice.CPU,
        "cuda": AcceleratorDevice.CUDA,
        "mps": AcceleratorDevice.MPS,
    }[args.device]
    opts.accelerator_options = AcceleratorOptions(num_threads=args.threads, device=device)

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )

    convert_kwargs = {}
    if args.max_pages:
        convert_kwargs["max_num_pages"] = args.max_pages
    result = converter.convert(args.input, **convert_kwargs)
    doc = result.document

    out = Path(args.output) if args.output else None

    if args.to == "md":
        md = doc.export_to_markdown()
        _emit(md, out)
    elif args.to == "text":
        _emit(doc.export_to_markdown(strict_text=True), out)
    elif args.to == "json":
        _emit(json.dumps(doc.export_to_dict(), indent=2, default=str), out)
    elif args.to == "tables":
        outdir = Path(args.output or "tables")
        outdir.mkdir(parents=True, exist_ok=True)
        for i, table in enumerate(doc.tables):
            df = table.export_to_dataframe(doc=doc)
            df.to_csv(outdir / f"table_{i + 1}.csv", index=False)
        sys.stderr.write(f"note: wrote {len(doc.tables)} table(s) to {outdir}/\n")
    elif args.to == "images":
        outdir = Path(args.output or "images")
        outdir.mkdir(parents=True, exist_ok=True)
        n = 0
        for i, pic in enumerate(doc.pictures):
            img = pic.get_image(doc)
            if img is not None:
                img.save(outdir / f"figure_{i + 1}.png")
                n += 1
        sys.stderr.write(f"note: wrote {n} figure(s) to {outdir}/\n")

    if args.images and args.to not in ("images",):
        # Also dump referenced images alongside a markdown export.
        md_out = out or Path(args.input).with_suffix(".md")
        doc.save_as_markdown(md_out, image_mode=ImageRefMode.REFERENCED)
        sys.stderr.write(f"note: wrote markdown + referenced images near {md_out}\n")
    return 0


# --------------------------------------------------------------------------- #
# pdfplumber engine (light fallback)
# --------------------------------------------------------------------------- #
def extract_pdfplumber(args) -> int:
    import pdfplumber

    if args.ocr:
        sys.stderr.write(
            "warning: --ocr requested but pdfplumber has no OCR; scanned pages "
            "will yield little text. Install docling for OCR.\n"
        )
    if args.images:
        sys.stderr.write("warning: --images not supported by pdfplumber engine.\n")

    out = Path(args.output) if args.output else None
    with pdfplumber.open(args.input) as pdf:
        pages = pdf.pages
        if args.max_pages:
            pages = pages[: args.max_pages]

        if args.to == "tables":
            import csv

            outdir = Path(args.output or "tables")
            outdir.mkdir(parents=True, exist_ok=True)
            # Financial reports rarely have ruled cells, so the default
            # line-based strategy yields empty tables. Fall back to a
            # text-alignment strategy, and drop tables that came out blank.
            settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "snap_y_tolerance": 5,
            }
            count = 0
            for pno, page in enumerate(pages, start=1):
                tables = page.extract_tables() or page.extract_tables(settings)
                for tno, table in enumerate(tables, start=1):
                    rows = [
                        [(c or "").strip() for c in row]
                        for row in table
                        if any((c or "").strip() for c in row)  # skip empty rows
                    ]
                    if not rows:
                        continue
                    with open(outdir / f"p{pno}_table_{tno}.csv", "w", newline="") as fh:
                        csv.writer(fh).writerows(rows)
                    count += 1
            if count == 0:
                sys.stderr.write(
                    "note: no tables recovered. Borderless/complex tables need "
                    "docling (TableFormer): `pip install docling` then "
                    "`--accurate-tables`.\n"
                )
            else:
                sys.stderr.write(f"note: wrote {count} table(s) to {outdir}/\n")
            return 0

        if args.to == "json":
            data = {
                "pages": [
                    {"page": i + 1, "text": (p.extract_text() or "")}
                    for i, p in enumerate(pages)
                ]
            }
            _emit(json.dumps(data, indent=2), out)
            return 0

        # md / text — pdfplumber has no layout model, so both are plain text.
        chunks = []
        for i, page in enumerate(pages, start=1):
            txt = page.extract_text() or ""
            if args.to == "md":
                chunks.append(f"<!-- page {i} -->\n\n{txt}")
            else:
                chunks.append(txt)
        _emit("\n\n".join(chunks), out)
    return 0


# --------------------------------------------------------------------------- #
def _emit(content: str, out: Path | None) -> None:
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        sys.stderr.write(f"note: wrote {out}\n")
    else:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="extract.py", description="Extract content from PDFs and documents."
    )
    p.add_argument("input", help="path to PDF/DOCX/XLSX/PPTX/HTML/image")
    p.add_argument("-o", "--output", help="output file or dir (stdout if omitted)")
    p.add_argument("--to", choices=["md", "text", "json", "tables", "images"],
                   default="md")
    p.add_argument("--engine", choices=["auto", "docling", "pdfplumber"],
                   default="auto")
    p.add_argument("--ocr", action="store_true", help="OCR scanned pages (docling)")
    p.add_argument("--lang", default="eng", help='OCR langs, e.g. "eng+fra"')
    p.add_argument("--accurate-tables", action="store_true",
                   help="TableFormer ACCURATE mode (slower, docling)")
    p.add_argument("--images", action="store_true", help="also extract figures (docling)")
    p.add_argument("--max-pages", type=int, help="only first N pages")
    p.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    p.add_argument("--threads", type=int, default=4)
    args = p.parse_args(argv)

    if not Path(args.input).is_file():
        sys.stderr.write(f"error: input file not found: {args.input}\n")
        return 1

    requested = args.engine
    if requested == "docling" and not _has("docling"):
        sys.stderr.write("error: docling not installed. pip install docling\n")
        return 2
    if requested == "auto" and not _has("docling"):
        sys.stderr.write(
            "note: docling not installed; using pdfplumber (no OCR / lower "
            "layout fidelity). `pip install docling` for full features.\n"
        )

    # Try docling when requested (or auto) and available. If it fails — some
    # valid PDFs (e.g. XeLaTeX output with Identity-H CID fonts) trip docling's
    # parser — fall back to pdfplumber in auto mode instead of hard-failing.
    if requested in ("docling", "auto") and _has("docling"):
        try:
            return extract_docling(args)
        except Exception as e:  # noqa: BLE001
            first = (str(e).splitlines() or [""])[0][:160]
            if requested == "docling":
                sys.stderr.write(
                    f"error: docling could not process this PDF "
                    f"({type(e).__name__}: {first}). Try --engine pdfplumber.\n"
                )
                return 1
            sys.stderr.write(
                f"note: docling could not parse this PDF ({type(e).__name__}); "
                f"falling back to pdfplumber.\n"
            )

    # pdfplumber path (explicit, or auto-fallback, or auto-without-docling)
    if not _has("pdfplumber"):
        sys.stderr.write("error: pdfplumber not installed. pip install pdfplumber\n")
        return 2
    try:
        return extract_pdfplumber(args)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"error: {type(e).__name__}: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
