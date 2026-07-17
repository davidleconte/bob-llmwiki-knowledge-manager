# `docling` CLI reference

The `docling` CLI ships with `pip install docling`. It covers conversion, OCR,
tables, VLM/ASR pipelines, enrichments, and (recent versions) chunking. Use it
for one-off jobs; use the skill scripts for figure extraction, RAG JSONL, batch,
structure analysis, and automation exit codes.

Official reference: <https://docling-project.github.io/docling/reference/cli/>

```bash
docling <SOURCE> [options]        # SOURCE = local path or URL; repeatable
```

## Input / output

| Flag | Values | Notes |
|---|---|---|
| `--from` | `pdf docx pptx xlsx html md asciidoc csv image xml_jats xml_uspto audio ...` | restrict/declare input formats (repeatable) |
| `--to` | `md json yaml html html_split_page text doctags vtt doclang dclx chunks` | output format (repeatable) |
| `--output DIR` | path | where files are written (named after the input) |
| `--image-export-mode` | `placeholder embedded referenced` | how images appear in md/html |
| `--show-layout` | flag | render layout debug overlay |

## Pipeline & models

| Flag | Values / default |
|---|---|
| `--pipeline` | `standard` (default) `vlm` `asr` |
| `--vlm-model` | `granite_docling` (default), `smoldocling`, … |
| `--asr-model` | `whisper_tiny` (default), `whisper_small`, `whisper_medium`, `whisper_turbo` |
| `--device` | `auto` (default) `cpu` `cuda` `mps` |
| `--num-threads` | int (default 4) |
| `--page-batch-size` | int |
| `--document-timeout` | seconds per document |

## OCR & tables

| Flag | Meaning |
|---|---|
| `--ocr` / `--no-ocr` | enable (default) / disable OCR |
| `--force-ocr` | OCR every page even with a text layer |
| `--ocr-engine` | `easyocr` (default) `rapidocr` `tesserocr` `tesseract` `ocrmac` |
| `--ocr-lang` | comma/plus list, e.g. `en,fr` or `eng+deu` |
| `--psm` | Tesseract page-segmentation mode |
| `--tables` / `--no-tables` | enable (default) / disable table structure |
| `--table-mode` | `fast` (default) `accurate` |
| `--pdf-backend` | `dlparse_v4` (default) `dlparse_v2` `pypdfium2` … |
| `--pdf-password` | password for encrypted PDFs |

## Enrichments (each pulls an extra model)

| Flag | Effect |
|---|---|
| `--enrich-code` | detect & tag code blocks |
| `--enrich-formula` | convert formulas to LaTeX |
| `--enrich-picture-classes` | classify figure types |
| `--enrich-picture-description` | caption figures (VLM; may need `--enable-remote-services`) |
| `--enrich-chart-extraction` | extract data from charts |

## Chunking (recent versions, `--to chunks`)

| Flag | Meaning |
|---|---|
| `--chunks-type` | `hybrid` (default) `hierarchical` |
| `--chunks-tokenizer` | HuggingFace tokenizer name/path (hybrid) |
| `--chunks-max-tokens` | token budget per chunk (hybrid) |

For RAG-ready JSONL with contextualized text + heading/page metadata, prefer
`scripts/docling_chunk.py` (this skill), which the CLI does not emit directly.

## Services, plugins, artifacts

| Flag | Meaning |
|---|---|
| `--enable-remote-services` | allow outbound HTTP (remote VLM, API enrichment) — off by default |
| `--allow-external-plugins` / `--show-external-plugins` | third-party pipeline plugins |
| `--artifacts-path` | local model directory (air-gapped) |

## Diagnostics

`-v/--verbose` (repeatable), `--debug-visualize-cells`, `--debug-visualize-ocr`,
`--debug-visualize-layout`, `--debug-visualize-tables`, `--abort-on-error`,
`--profiling`, `--version`.

## Model management (`docling-tools`)

```bash
docling-tools models download                 # pre-fetch all models (offline prep)
docling-tools models download-hf-repo <repo>  # fetch a specific HF model repo
```

## Common one-liners

```bash
docling report.pdf --output ./out/                                  # → report.md
docling report.pdf --to json --output ./out/                        # lossless JSON
docling scan.pdf --force-ocr --ocr-engine tesseract --output ./out/
docling paper.pdf --pipeline vlm --output ./out/
docling talk.mp4 --pipeline asr --to vtt --output ./out/            # subtitles
docling secret.pdf --pdf-password 's3cret' --output ./out/
docling invoice.pdf --table-mode accurate --to md --output ./out/
```
