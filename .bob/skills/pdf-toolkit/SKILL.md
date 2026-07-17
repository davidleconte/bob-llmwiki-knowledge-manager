---
name: pdf-toolkit
description: >
  Swiss-army knife for PDFs. Use whenever the user wants to read, parse, extract
  (text / tables / figures / OCR), convert to Markdown/HTML/JSON, or manipulate
  PDFs (merge, split, rotate, watermark, encrypt/decrypt, edit metadata, extract
  images, compress, list/fill forms), OR generate a new professional PDF from
  Markdown. Three tiers: light pure-python (pypdf/pikepdf/pdfplumber) for fast
  manipulation & extraction, Docling (IBM Research) for high-fidelity layout /
  tables / OCR / RAG, and Pandoc + Eisvogel for themed PDF generation.
---

# PDF Toolkit

A production PDF toolkit built around **three deterministic CLI scripts** plus a
library reference for cases the scripts don't cover.

> **Prefer the scripts.** They validate input, handle encryption, degrade
> gracefully when a heavy dependency is missing, and return clean exit codes
> (`0` ok · `1` runtime/usage error · `2` missing dependency). Only drop to
> raw library code for something a script flag can't express.

| Script | Does | Engine |
|---|---|---|
| [`pdf_ops.py`](scripts/pdf_ops.py) | merge · split · pages · rotate · watermark · encrypt · decrypt · meta · images · compress · fields · fill | pypdf + pikepdf |
| [`extract.py`](scripts/extract.py) | text · markdown · json · tables · figures · OCR | Docling → pdfplumber fallback |
| [`generate_pdf.py`](scripts/generate_pdf.py) | Markdown → themed PDF (A4 / mobile / Russian) | Pandoc + Eisvogel |
| [`md_to_pdf.py`](scripts/md_to_pdf.py) | Markdown → PDF, zero system deps (light fallback) | reportlab |
| [`fix_markdown.py`](scripts/fix_markdown.py) | pre-process Markdown lists before generation | stdlib |
| [`selftest.sh`](scripts/selftest.sh) | verify the whole install in one command | bash |

## Decision guide

```
What does the user want?
│
├─ Change an existing PDF's structure (combine, cut, secure, stamp, forms)?
│     → pdf_ops.py                                              (Part 1)
│
├─ Get the CONTENT out of a PDF (text, tables, figures, RAG chunks, OCR)?
│     → extract.py  (or Docling library for advanced pipelines) (Part 2)
│
└─ Produce a NEW PDF from Markdown / text?
      → generate_pdf.py  (Pandoc)  or  pure-python fallback     (Part 3)
```

## Setup (tiered — install only what the task needs)

```bash
pip install -r requirements.txt          # tier 1+2 baseline
# tier 3 (heavy, ML — layout/tables/OCR/RAG). Large download, pulls torch:
pip install "docling>=2.0"
# generation via LaTeX (optional; pure-python fallback exists — see Part 3):
brew install pandoc && brew install --cask mactex
```

Check what's available before choosing a path:

```bash
python3 -c "import pypdf, pikepdf, pdfplumber" 2>/dev/null && echo "tier1 ok"
python3 -c "import docling" 2>/dev/null && echo "docling ok"
command -v pandoc >/dev/null && echo "pandoc ok"
```

`extract.py --engine auto` (the default) will use Docling if importable and
otherwise fall back to pdfplumber, printing a note — so extraction never hard-fails
just because the heavy tier isn't installed.

**Verify the install** at any time:

```bash
bash scripts/selftest.sh      # generates a sample PDF, exercises the core ops
```

---

## Part 1 — Manipulate PDFs (`pdf_ops.py`)

All page ranges are **1-based, inclusive**: `"1-3,5,8-10"` or `"all"`.
Pass `--password PW` (before the subcommand) for encrypted inputs.

```bash
# Inspect
python3 scripts/pdf_ops.py info report.pdf

# Combine / cut
python3 scripts/pdf_ops.py merge a.pdf b.pdf c.pdf -o combined.pdf
python3 scripts/pdf_ops.py split big.pdf --outdir pages/           # one file per page
python3 scripts/pdf_ops.py split big.pdf --chunk 10 --outdir parts/ # 10-page chunks
python3 scripts/pdf_ops.py pages report.pdf "1-3,7" -o excerpt.pdf  # extract/reorder

# Transform
python3 scripts/pdf_ops.py rotate scan.pdf -o fixed.pdf --degrees 90 --range "2,4"
python3 scripts/pdf_ops.py watermark report.pdf --stamp confidential.pdf -o stamped.pdf
python3 scripts/pdf_ops.py compress huge.pdf -o small.pdf           # stream compress + linearize

# Security
python3 scripts/pdf_ops.py encrypt report.pdf -o locked.pdf --user-password s3cret
python3 scripts/pdf_ops.py --password s3cret decrypt locked.pdf -o open.pdf

# Metadata
python3 scripts/pdf_ops.py meta report.pdf                          # print current
python3 scripts/pdf_ops.py meta report.pdf --set Title="Q3 Report" Author="F. Manaila" -o out.pdf

# Images & forms
python3 scripts/pdf_ops.py images report.pdf --outdir figures/
python3 scripts/pdf_ops.py fields form.pdf                          # list AcroForm fields
python3 scripts/pdf_ops.py fill form.pdf --data values.json -o filled.pdf
```

**Watermark note:** `--stamp` must be a single-page PDF sized like the target
(create one with `generate_pdf.py` or reportlab). It's overlaid on every page.

**Encryption note:** uses AES-256. If `--owner-password` is omitted it defaults to
the user password. Losing both means the file cannot be reopened.

---

## Part 2 — Read / Extract (`extract.py` + Docling)

### 2.1 The script (start here)

```bash
python3 scripts/extract.py doc.pdf --to md                 # Markdown to stdout
python3 scripts/extract.py doc.pdf --to md -o doc.md        # to file
python3 scripts/extract.py doc.pdf --to text                # plain text
python3 scripts/extract.py doc.pdf --to json -o doc.json    # lossless structure (docling)
python3 scripts/extract.py doc.pdf --to tables -o tables/   # one CSV per table
python3 scripts/extract.py scan.pdf --ocr --lang "eng+fra"  # OCR a scanned PDF (docling)
python3 scripts/extract.py paper.pdf --to md --images       # md + referenced figures (docling)
python3 scripts/extract.py doc.pdf --engine pdfplumber      # force the light engine
python3 scripts/extract.py doc.pdf --accurate-tables        # slower, better tables (docling)
```

Docling also accepts DOCX, XLSX, PPTX, HTML, and images as input — same command.

### 2.2 Docling library — verified API (for pipelines the script can't express)

> The snippets below are the **correct current Docling 2.x API**. Common wrong
> patterns to avoid: `DocumentConverter(pipeline_options=...)` (must go through
> `format_options`), `OcrOptions(use_gpu=...)`, `doc.headings`/`doc.paragraphs`,
> `table.to_markdown()`, `pic.save()`. None of those exist.

**Configured conversion:**

```python
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption

opts = PdfPipelineOptions()
opts.do_ocr = True
opts.do_table_structure = True
opts.table_structure_options.mode = TableFormerMode.ACCURATE   # or .FAST
opts.table_structure_options.do_cell_matching = True
opts.ocr_options.lang = ["en"]                                 # a LIST
opts.accelerator_options = AcceleratorOptions(
    num_threads=4, device=AcceleratorDevice.AUTO,              # AUTO|CPU|CUDA|MPS
)
# optional enrichments:
opts.do_code_enrichment = True        # detect code blocks
opts.do_formula_enrichment = True     # formulas -> LaTeX

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
)

# Per-call limits live on convert(), NOT the constructor:
result = converter.convert("doc.pdf", max_num_pages=100, max_file_size=50_000_000)
doc = result.document
```

**Exports:**

```python
doc.export_to_markdown()                       # LLM-friendly Markdown
doc.export_to_markdown(strict_text=True)        # plain text, no markup
doc.export_to_dict()                            # lossless: bbox, hierarchy, confidence
doc.export_to_doctags()                         # DocTags serialization

from docling_core.types.doc import ImageRefMode
doc.save_as_markdown("out.md", image_mode=ImageRefMode.REFERENCED)  # writes image files
doc.save_as_html("out.html", image_mode=ImageRefMode.EMBEDDED)      # base64 inline
```

**Tables → pandas / CSV / HTML:**

```python
for i, table in enumerate(doc.tables):
    df = table.export_to_dataframe(doc=doc)     # pandas DataFrame
    df.to_csv(f"table_{i}.csv", index=False)
    md = df.to_markdown()
    html = table.export_to_html(doc=doc)
```

**Figures & page images** (require `opts.generate_picture_images = True`,
`opts.generate_page_images = True`, `opts.images_scale = 2.0`):

```python
for i, pic in enumerate(doc.pictures):
    img = pic.get_image(doc)                    # PIL.Image or None
    if img:
        img.save(f"figure_{i}.png")
for page in doc.pages.values():                 # pages is a dict {page_no: PageItem}
    page.image.pil_image.save(f"page_{page.page_no}.png")
```

**Walk the structure:**

```python
from docling_core.types.doc import TextItem, TableItem, PictureItem
for item, level in doc.iterate_items():         # depth-first, reading order
    if isinstance(item, TextItem):
        print(item.label, item.text)            # label: title/section_header/text/...
    elif isinstance(item, TableItem):
        ...
```

**OCR engine selection** (EasyOCR is default; Tesseract needs the binary):

```python
from docling.datamodel.pipeline_options import TesseractCliOcrOptions
opts.ocr_options = TesseractCliOcrOptions(lang=["eng", "fra"])
opts.ocr_options.force_full_page_ocr = True     # OCR even pages with a text layer
```

**Choose PDF backend** (default is DoclingParse v4; pypdfium is an alternative):

```python
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=opts,
                                     backend=PyPdfiumDocumentBackend)
})
```

### 2.3 RAG chunking (verified API)

```python
from docling.chunking import HybridChunker
chunker = HybridChunker(
    tokenizer="sentence-transformers/all-MiniLM-L6-v2",
    max_tokens=512,
    merge_peers=True,
)
for chunk in chunker.chunk(dl_doc=doc):
    text = chunker.contextualize(chunk=chunk)   # prepends section headings
    meta = chunk.meta
```

### 2.4 LangChain / LlamaIndex

```python
# pip install langchain-docling
from langchain_docling import DoclingLoader
docs = DoclingLoader(file_path="manual.pdf").load()

# pip install llama-index-readers-docling llama-index-node-parser-docling
from llama_index.readers.docling import DoclingReader
from llama_index.node_parser.docling import DoclingNodeParser
reader_docs = DoclingReader().load_data("paper.pdf")
```

### 2.5 Offline / air-gapped

```bash
docling-tools models download                   # pre-fetch models
export DOCLING_ARTIFACTS_PATH=/path/to/models    # point at them
export OMP_NUM_THREADS=8                          # CPU thread control
```

There is also an official MCP server (`docling-mcp`, repo
`docling-project/docling-mcp`) for agentic use — check the repo for the current
launch command, as it changes between releases.

---

## Part 3 — Generate a PDF from Markdown

### 3.1 Pandoc + Eisvogel (`generate_pdf.py`) — best quality

```bash
python3 scripts/generate_pdf.py doc.md                          # A4, TOC
python3 scripts/generate_pdf.py doc.md -e -t white-paper         # themed title page (Eisvogel)
python3 scripts/generate_pdf.py doc.md --mobile                  # 6×9in phone/Telegram layout
python3 scripts/generate_pdf.py doc-ru.md --russian              # EB Garamond (Cyrillic)
python3 scripts/generate_pdf.py doc.md -o out/report.pdf
```

The actual theme is driven by the `titlepage-color` in the document's YAML front
matter (the `-t` flag is just a label). Use the Client Engineering deliverable
templates — Discovery Brief, PoC Report, Solution Blueprint, Executive Summary,
Sprint Readout, with the IBM Carbon palette — in
[references/frontmatter_templates.md](references/frontmatter_templates.md).

> **`-e/--eisvogel` is required for title pages / theme colors.** The
> `titlepage: true` and `titlepage-color:` YAML settings only take effect when the
> Eisvogel template is applied. Install it once from the release tarball (the
> self-contained top-level `eisvogel.latex` — the `template-multi-file/` copy needs
> extra includes and will error with "Could not find … eisvogel-added.latex"):
> ```bash
> mkdir -p ~/.local/share/pandoc/templates
> tmp=$(mktemp -d)
> curl -L -o "$tmp/eis.tar.gz" \
>   https://github.com/Wandmalfarbe/pandoc-latex-template/releases/latest/download/Eisvogel.tar.gz
> tar -xzf "$tmp/eis.tar.gz" -C "$tmp"
> cp "$tmp"/Eisvogel-*/eisvogel.latex ~/.local/share/pandoc/templates/eisvogel.latex
> ```
> On macOS, ensure the TeX binaries are on PATH (`export PATH="$PATH:/Library/TeX/texbin"`)
> and that `pandoc` is installed (`brew install pandoc`) — MacTeX alone provides
> XeLaTeX but not Pandoc.

If Markdown lists render inline (a common LLM-output issue), pre-process first:

```bash
python3 scripts/fix_markdown.py input.md fixed.md
```

### 3.2 Pure-python fallback (`md_to_pdf.py`) — no LaTeX, no system libs

When Pandoc/MacTeX (~4 GB) aren't available, use `md_to_pdf.py`, which needs only
`reportlab`. Ideal for CI, containers, and "summarize a PDF into a new PDF":

```bash
pip install reportlab
python3 scripts/md_to_pdf.py summary.md -o summary.pdf --accent 0f62fe
```

Supports headings, paragraphs, bullet/numbered lists, code fences, blockquotes,
rules, inline **bold**/*italic*/`code`, and a YAML-front-matter title block. It
renders list markers as ASCII so the **generated PDF's text layer stays clean and
re-extractable** (a plain `weasyprint`/reportlab bullet re-extracts as `(cid:127)`).

For themed title pages and print-grade typography, prefer Pandoc (3.1). `md_to_pdf.py`
is the dependency-light workhorse; it does not do LaTeX-quality layout or tables.

---

## Production notes

- **Validate first.** Run `pdf_ops.py info` before manipulating — it reveals page
  count and, crucially, whether the file is encrypted (encrypted inputs need
  `--password`).
- **Encrypted inputs** are detected by every `pdf_ops.py` command; without a
  password they exit `1` with a clear message rather than a traceback.
- **Large / untrusted PDFs:** cap work with `extract.py --max-pages N`, or Docling's
  `convert(..., max_num_pages=, max_file_size=)`. Docling's ML pipeline is memory-
  heavy — process in batches and `gc.collect()` between them.
- **Determinism:** the scripts write byte-stable output for the same input; safe to
  use in pipelines and to diff.
- **Exit codes:** `0` success · `1` runtime/usage error · `2` missing dependency
  (with a `pip install` hint). Check them in automation.
- **Fidelity vs. cost:** pdfplumber is instant but has no OCR and weaker table/layout
  reconstruction; Docling is far more accurate but heavy. `--engine auto` picks the
  best available and tells you which it used.

## Troubleshooting

| Problem | Fix |
|---|---|
| `'pypdf' is required` (exit 2) | `pip install pypdf pikepdf` |
| Extraction returns empty text | Scanned/image PDF — add `--ocr` (needs docling) |
| `docling not installed; using pdfplumber` | Expected fallback; `pip install docling` for OCR/layout |
| Docling models fail to download | `docling-tools models download`; set `DOCLING_ARTIFACTS_PATH` |
| Docling OOM on big PDF | `convert(..., max_num_pages=, max_file_size=)`; batch + `gc.collect()` |
| Wrong table structure | `--accurate-tables` (script) / `TableFormerMode.ACCURATE` |
| Empty/garbled tables from pdfplumber | Expected on borderless (e.g. financial) tables — install docling and use `--accurate-tables`; pdfplumber has no layout model |
| `docling could not parse this PDF (ConversionError)` | Some valid PDFs (e.g. XeLaTeX output with Identity-H CID fonts) trip docling's parser. `--engine auto` auto-falls-back to pdfplumber; force it with `--engine pdfplumber` |
| Encrypted input error | pass `--password` before the subcommand |
| Title page / theme not showing | pass `-e/--eisvogel` and install the template (3.1) |
| `pandoc: command not found` | `brew install pandoc` — or use the pure-python fallback (3.2) |
| XeLaTeX not found | `brew install --cask mactex`, restart shell |
| Russian text renders as boxes | add `--russian` (EB Garamond) |
| Lists render inline in generated PDF | run `fix_markdown.py` first |

## Resources

- Docling docs — https://docling-project.github.io/docling/
- Docling GitHub — https://github.com/docling-project/docling
- pypdf docs — https://pypdf.readthedocs.io/
- pikepdf docs — https://pikepdf.readthedocs.io/
- pdfplumber — https://github.com/jsvine/pdfplumber
- Pandoc manual — https://pandoc.org/MANUAL.html
- Eisvogel template — https://github.com/Wandmalfarbe/pandoc-latex-template
- [references/pandoc_reference.md](references/pandoc_reference.md) · [references/frontmatter_templates.md](references/frontmatter_templates.md)
