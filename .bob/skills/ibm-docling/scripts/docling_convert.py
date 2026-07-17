#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
docling_convert.py — the workhorse: convert ANY Docling-supported source into a
target format with full control over OCR, tables, pipeline, enrichments, and
image export. Wraps the Docling Python API so an agent gets deterministic exit
codes and a compact JSON summary on stderr-free stdout is avoided (summary goes
to stderr; the converted document goes to the output file or stdout).

Supported inputs  : PDF, DOCX, PPTX, XLSX, HTML, Markdown, AsciiDoc, CSV,
                    images (png/jpg/tiff/...), XML (JATS/USPTO), audio/video
                    (with --pipeline asr), and a URL to any of these.
Supported outputs : md | text | json | yaml | html | doctags

Pipelines         : standard (default) | vlm | asr
OCR engines       : easyocr (default) | rapidocr | tesserocr | tesseract | ocrmac

Exit codes: 0 ok · 1 runtime/usage error · 2 missing dependency (pip hint given).

Prefer the plain `docling` CLI for one-off conversions (it exposes the same
knobs); use this script when you want a single call that also extracts figures,
emits a machine-readable summary, and returns clean exit codes for automation.
"""
from __future__ import annotations

import argparse
import json
import logging
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


def _summary(payload: dict) -> None:
    """Emit a one-line JSON summary to stderr so stdout stays clean for content."""
    sys.stderr.write("summary: " + json.dumps(payload, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- #
# Pipeline option builders
# --------------------------------------------------------------------------- #
def _accelerator(args):
    from docling.datamodel.accelerator_options import (
        AcceleratorDevice,
        AcceleratorOptions,
    )

    device = {
        "auto": AcceleratorDevice.AUTO,
        "cpu": AcceleratorDevice.CPU,
        "cuda": AcceleratorDevice.CUDA,
        "mps": AcceleratorDevice.MPS,
    }[args.device]
    return AcceleratorOptions(num_threads=args.threads, device=device)


def _ocr_options(args):
    """Return an OcrOptions instance for the chosen engine, or None for default."""
    langs = args.ocr_lang.split("+") if args.ocr_lang else None
    engine = args.ocr_engine
    if engine in (None, "easyocr"):
        from docling.datamodel.pipeline_options import EasyOcrOptions

        opts = EasyOcrOptions()
    elif engine == "rapidocr":
        from docling.datamodel.pipeline_options import RapidOcrOptions

        opts = RapidOcrOptions()
    elif engine == "tesserocr":
        from docling.datamodel.pipeline_options import TesseractOcrOptions

        opts = TesseractOcrOptions()
    elif engine == "tesseract":
        from docling.datamodel.pipeline_options import TesseractCliOcrOptions

        opts = TesseractCliOcrOptions()
    elif engine == "ocrmac":
        from docling.datamodel.pipeline_options import OcrMacOptions

        opts = OcrMacOptions()
    else:  # pragma: no cover - argparse restricts choices
        raise ValueError(f"unknown ocr engine: {engine}")

    if langs:
        opts.lang = langs
    if args.force_ocr:
        opts.force_full_page_ocr = True
    return opts


def _standard_pdf_options(args):
    from docling.datamodel.pipeline_options import (
        PdfPipelineOptions,
        TableFormerMode,
    )

    opts = PdfPipelineOptions()
    opts.do_ocr = not args.no_ocr
    opts.do_table_structure = not args.no_tables
    opts.table_structure_options.mode = (
        TableFormerMode.ACCURATE if args.accurate_tables else TableFormerMode.FAST
    )
    opts.table_structure_options.do_cell_matching = True
    if opts.do_ocr:
        opts.ocr_options = _ocr_options(args)

    # Enrichments (each pulls an extra model on first use).
    opts.do_code_enrichment = args.enrich_code
    opts.do_formula_enrichment = args.enrich_formula
    opts.do_picture_classification = args.enrich_picture_classes
    opts.do_picture_description = args.enrich_picture_description

    # Image generation is required to export figures / page images.
    if args.images or args.to in ("html",):
        opts.generate_picture_images = True
        opts.generate_page_images = True
        opts.images_scale = args.image_scale

    opts.accelerator_options = _accelerator(args)
    if args.remote:
        opts.enable_remote_services = True
    return opts


def _build_converter(args):
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption

    if args.pipeline == "vlm":
        from docling.datamodel import vlm_model_specs
        from docling.datamodel.pipeline_options import VlmPipelineOptions
        from docling.pipeline.vlm_pipeline import VlmPipeline

        preset = {
            "granite_docling": "GRANITEDOCLING_TRANSFORMERS",
            "smoldocling": "SMOLDOCLING_TRANSFORMERS",
            "granite_docling_mlx": "GRANITEDOCLING_MLX",
            "granite_docling_vllm": "GRANITEDOCLING_VLLM",
        }[args.vlm_model]
        vlm_options = getattr(vlm_model_specs, preset)
        pipe_opts = VlmPipelineOptions(
            vlm_options=vlm_options,
            generate_page_images=True,
        )
        if args.force_backend_text:
            pipe_opts.force_backend_text = True
        if args.remote:
            pipe_opts.enable_remote_services = True
        pdf_format = PdfFormatOption(
            pipeline_cls=VlmPipeline, pipeline_options=pipe_opts
        )
    else:
        pdf_format = PdfFormatOption(pipeline_options=_standard_pdf_options(args))

    # PDF and IMAGE share the PDF-style pipeline options.
    format_options = {
        InputFormat.PDF: pdf_format,
        InputFormat.IMAGE: pdf_format,
    }
    return DocumentConverter(format_options=format_options)


def _build_asr_converter(args):
    """Audio / video transcription via the ASR (Whisper) pipeline."""
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import AsrPipelineOptions
    from docling.datamodel import asr_model_specs
    from docling.document_converter import AudioFormatOption, DocumentConverter
    from docling.pipeline.asr_pipeline import AsrPipeline

    preset = {
        "whisper_tiny": "WHISPER_TINY",
        "whisper_small": "WHISPER_SMALL",
        "whisper_medium": "WHISPER_MEDIUM",
        "whisper_turbo": "WHISPER_TURBO",
    }[args.asr_model]
    pipe_opts = AsrPipelineOptions(asr_options=getattr(asr_model_specs, preset))
    return DocumentConverter(
        format_options={
            InputFormat.AUDIO: AudioFormatOption(
                pipeline_cls=AsrPipeline, pipeline_options=pipe_opts
            )
        }
    )


# --------------------------------------------------------------------------- #
# Export
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


def _export(doc, args) -> None:
    out = Path(args.output) if args.output else None

    if args.to == "md":
        if args.images and out is not None:
            from docling_core.types.doc import ImageRefMode

            doc.save_as_markdown(out, image_mode=ImageRefMode.REFERENCED)
            sys.stderr.write(f"note: wrote {out} + referenced image files\n")
        else:
            _emit(doc.export_to_markdown(), out)
    elif args.to == "text":
        _emit(doc.export_to_markdown(strict_text=True), out)
    elif args.to == "json":
        _emit(json.dumps(doc.export_to_dict(), indent=2, default=str, ensure_ascii=False), out)
    elif args.to == "yaml":
        import yaml  # PyYAML ships with docling

        _emit(yaml.safe_dump(doc.export_to_dict(), sort_keys=False, allow_unicode=True), out)
    elif args.to == "html":
        from docling_core.types.doc import ImageRefMode

        if out is not None:
            doc.save_as_html(out, image_mode=ImageRefMode.EMBEDDED)
            sys.stderr.write(f"note: wrote {out}\n")
        else:
            _emit(doc.export_to_html(), None)
    elif args.to == "doctags":
        _emit(doc.export_to_doctags(), out)

    # Optionally dump figures as separate PNGs regardless of output format.
    if args.images and args.to != "md":
        outdir = Path(args.image_dir or (out.parent if out else Path("."))) / "figures"
        outdir.mkdir(parents=True, exist_ok=True)
        n = 0
        for i, pic in enumerate(doc.pictures):
            img = pic.get_image(doc)
            if img is not None:
                img.save(outdir / f"figure_{i + 1}.png")
                n += 1
        sys.stderr.write(f"note: wrote {n} figure(s) to {outdir}/\n")


# --------------------------------------------------------------------------- #
def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="docling_convert.py",
        description="Convert any Docling-supported document to md/text/json/yaml/html/doctags.",
    )
    p.add_argument("source", help="local path or URL to the document (or audio/video for --pipeline asr)")
    p.add_argument("-o", "--output", help="output file (stdout if omitted)")
    p.add_argument(
        "--to",
        choices=["md", "text", "json", "yaml", "html", "doctags"],
        default="md",
        help="output format (default: md)",
    )
    p.add_argument(
        "--pipeline",
        choices=["standard", "vlm", "asr"],
        default="standard",
        help="processing pipeline (default: standard)",
    )

    ocr = p.add_argument_group("OCR (standard pipeline)")
    ocr.add_argument("--no-ocr", action="store_true", help="skip OCR entirely (faster on born-digital PDFs)")
    ocr.add_argument("--force-ocr", action="store_true", help="OCR every page even if it has a text layer")
    ocr.add_argument(
        "--ocr-engine",
        choices=["easyocr", "rapidocr", "tesserocr", "tesseract", "ocrmac"],
        default="easyocr",
    )
    ocr.add_argument("--ocr-lang", default=None, help='OCR languages, e.g. "en+fr" or "eng+deu"')

    tables = p.add_argument_group("Tables (standard pipeline)")
    tables.add_argument("--no-tables", action="store_true", help="skip table-structure detection")
    tables.add_argument("--accurate-tables", action="store_true", help="TableFormer ACCURATE (slower, better)")

    enrich = p.add_argument_group("Enrichments (standard pipeline; each pulls a model)")
    enrich.add_argument("--enrich-code", action="store_true", help="detect & tag code blocks")
    enrich.add_argument("--enrich-formula", action="store_true", help="convert formulas to LaTeX")
    enrich.add_argument("--enrich-picture-classes", action="store_true", help="classify figure types")
    enrich.add_argument("--enrich-picture-description", action="store_true", help="caption figures (VLM)")

    vlm = p.add_argument_group("VLM pipeline")
    vlm.add_argument(
        "--vlm-model",
        choices=["granite_docling", "smoldocling", "granite_docling_mlx", "granite_docling_vllm"],
        default="granite_docling",
    )
    vlm.add_argument(
        "--force-backend-text",
        action="store_true",
        help="hybrid: deterministic text for text regions, VLM only for images/tables",
    )

    asr = p.add_argument_group("ASR pipeline (audio/video)")
    asr.add_argument(
        "--asr-model",
        choices=["whisper_tiny", "whisper_small", "whisper_medium", "whisper_turbo"],
        default="whisper_tiny",
    )

    imgs = p.add_argument_group("Images")
    imgs.add_argument("--images", action="store_true", help="also export figures / embed page images")
    imgs.add_argument("--image-dir", default=None, help="directory for extracted figures")
    imgs.add_argument("--image-scale", type=float, default=2.0, help="render scale for images (default 2.0)")

    perf = p.add_argument_group("Runtime")
    perf.add_argument("--device", choices=["auto", "cpu", "cuda", "mps"], default="auto")
    perf.add_argument("--threads", type=int, default=4)
    perf.add_argument("--max-pages", type=int, help="only process the first N pages")
    perf.add_argument("--max-file-size", type=int, help="reject inputs larger than N bytes")
    perf.add_argument("--timeout", type=float, help="abort a single document after N seconds")
    perf.add_argument("--password", help="password for encrypted PDFs")
    perf.add_argument("--remote", action="store_true", help="allow outbound HTTP (remote VLM/enrichment)")
    perf.add_argument("--quiet", action="store_true", help="silence docling's per-page logging")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if not _has("docling"):
        return _die(
            "error: docling is not installed. Run: pip install docling docling-core",
            2,
        )

    if args.quiet:
        logging.getLogger("docling").setLevel(logging.CRITICAL)

    # Local file existence check (URLs are passed through to docling).
    is_url = "://" in args.source
    if not is_url and not Path(args.source).exists():
        return _die(f"error: source not found: {args.source}", 1)

    try:
        if args.pipeline == "asr":
            converter = _build_asr_converter(args)
        else:
            converter = _build_converter(args)

        convert_kwargs: dict = {}
        if args.max_pages:
            convert_kwargs["max_num_pages"] = args.max_pages
        if args.max_file_size:
            convert_kwargs["max_file_size"] = args.max_file_size
        # Encrypted PDFs are handled most reliably by the CLI's --pdf-password.
        if args.password and not is_url:
            sys.stderr.write(
                "note: for password-protected PDFs prefer the CLI: "
                "docling <src> --pdf-password <PW> --output <dir>\n"
            )
        result = converter.convert(args.source, **convert_kwargs)
        doc = result.document
    except Exception as e:  # noqa: BLE001
        first = (str(e).splitlines() or [""])[0][:200]
        return _die(
            f"error: conversion failed ({type(e).__name__}: {first}). "
            f"See references/troubleshooting.md.",
            1,
        )

    _export(doc, args)

    n_pages = len(getattr(doc, "pages", {}) or {})
    _summary(
        {
            "source": args.source,
            "pipeline": args.pipeline,
            "to": args.to,
            "pages": n_pages,
            "tables": len(getattr(doc, "tables", []) or []),
            "pictures": len(getattr(doc, "pictures", []) or []),
            "output": args.output or "<stdout>",
            "status": "ok",
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
