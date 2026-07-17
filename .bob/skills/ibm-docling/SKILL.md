---
name: ibm-docling
description: >
  Production document intelligence with Docling (IBM Research). Use whenever the
  user provides a document — PDF, DOCX, PPTX, XLSX, HTML, Markdown, AsciiDoc,
  CSV, an image (PNG/JPG/TIFF), XML (JATS/USPTO), or audio/video — as a local
  path or URL and wants to: convert it to Markdown / JSON (DoclingDocument) /
  HTML / DocTags / plain text, OCR a scan, run a vision-language (VLM) pipeline
  for complex layouts / handwriting / formulas, transcribe audio/video (ASR),
  extract tables or figures, enrich (code, formulas, figure captions/classes),
  chunk for RAG ingestion, analyze document structure, batch-convert a folder,
  or evaluate and improve conversion quality. Triggers: "parse this PDF",
  "convert to markdown", "extract the tables", "OCR this scan", "chunk for RAG",
  "prepare for ingestion", "transcribe this recording", "analyze document
  structure", "process document", "docling".
license: MIT
compatibility: Requires Python 3.10+, docling>=2.55, docling-core>=2.60
metadata:
  author: ibm-docling skill for Bob
  version: "1.0"
  upstream: https://github.com/docling-project/docling
allowed-tools: Bash(docling:*) Bash(docling-tools:*) Bash(python3:*) Bash(pip:*)
---

# ibm-docling — Document Intelligence

Docling converts almost any document into a single, structured
`DoclingDocument` you can export to Markdown, lossless JSON, HTML, DocTags, or
plain text — with OCR, table structure, figures, enrichments, RAG chunking, and
speech transcription. This skill wraps that with **five deterministic scripts**
plus a **verified CLI + Python reference**, so conversions are reproducible and
the agent never guesses the API.

> **Two equivalent front doors.** For a one-off conversion, the plain `docling`
> CLI is the shortest path and exposes every knob. Use the **scripts** when you
> want figure extraction, a machine-readable summary, batch processing, RAG
> JSONL, structure analysis, or clean exit codes for automation. They call the
> same engine.

Exit codes for every script: **`0`** ok · **`1`** runtime/usage error ·
**`2`** missing dependency (prints the exact `pip install`).

## Decision guide

```
What does the user want?
│
├─ Turn a document INTO text/markdown/json/html?         → docling_convert.py   (Part 1)
│     ├─ born-digital PDF / Office / HTML                 → --pipeline standard (default)
│     ├─ scanned / photographed / image-only             → --force-ocr  (pick --ocr-engine)
│     ├─ complex layout / multi-column / handwriting /
│     │  formulas / bad reading order                     → --pipeline vlm
│     └─ audio or video recording                         → --pipeline asr
│
├─ Get the TABLES or FIGURES out?                         → docling_convert.py --images / analyze (Part 2)
│
├─ Prepare it for RAG / a vector DB?                      → docling_chunk.py     (Part 3)
│
├─ Understand its STRUCTURE (outline, table/figure map)?  → docling_analyze.py   (Part 4)
│
├─ Process a whole FOLDER of documents?                   → docling_batch.py     (Part 5)
│
└─ Is the conversion GOOD ENOUGH? improve it?             → docling_evaluate.py  (Part 6, the loop)
```

## Setup

```bash
pip install -r requirements.txt      # tier 1: convert + OCR + tables + chunk (CPU)
bash scripts/selftest.sh             # verify the whole install end to end
```

Heavier tiers are opt-in — install only when the task needs them:

```bash
pip install "docling[vlm]"                       # VLM pipeline (torch + transformers)
pip install mlx mlx-lm                            # Apple-Silicon VLM acceleration
pip install "docling[asr]"                        # audio/video transcription
pip install "docling-core[chunking-openai]"       # OpenAI (tiktoken) chunking
```

Check what's available before choosing a path:

```bash
python3 -c "import docling, docling_core; print('core ok')"
python3 -c "import torch, transformers; print('vlm ok')" 2>/dev/null || echo "vlm not installed"
command -v docling >/dev/null && echo "cli ok"
```

Supported inputs and outputs are enumerated in
[references/formats.md](references/formats.md).

---

## Part 1 — Convert (`docling_convert.py`)

The workhorse. Any supported input → `md` (default) · `text` · `json` · `yaml`
· `html` · `doctags`. Accepts a local path **or a URL**.

```bash
# Markdown to a file (summary printed to stderr as `summary: {...}`)
python3 scripts/docling_convert.py report.pdf --to md -o report.md

# Lossless structured JSON (a DoclingDocument: bbox, hierarchy, provenance)
python3 scripts/docling_convert.py report.pdf --to json -o report.json

# From a URL, straight to stdout
python3 scripts/docling_convert.py https://arxiv.org/pdf/2408.09869 --to md

# Office / HTML / image inputs use the same command
python3 scripts/docling_convert.py deck.pptx --to md -o deck.md
python3 scripts/docling_convert.py page.html --to md -o page.md
```

### OCR (scanned / image PDFs)

OCR is **on by default** in the standard pipeline (it OCRs bitmap regions).
Force it for full-page scans; pick an engine and languages as needed.

```bash
python3 scripts/docling_convert.py scan.pdf --force-ocr -o scan.md
python3 scripts/docling_convert.py scan.pdf --force-ocr --ocr-engine tesseract --ocr-lang "eng+deu" -o scan.md
python3 scripts/docling_convert.py born_digital.pdf --no-ocr -o fast.md   # skip OCR for speed
```

Engines: `easyocr` (default, no extra install) · `rapidocr` · `tesserocr` ·
`tesseract` (CLI) · `ocrmac` (macOS). Details:
[references/pipelines.md](references/pipelines.md).

### Tables

Table structure detection is on by default (TableFormer). Use `--accurate-tables`
for merged cells / dense financial tables; `--no-tables` to skip for speed.

```bash
python3 scripts/docling_convert.py invoice.pdf --accurate-tables --to md -o invoice.md
```

### VLM pipeline (complex layout, handwriting, formulas)

```bash
python3 scripts/docling_convert.py paper.pdf --pipeline vlm -o paper.md
python3 scripts/docling_convert.py paper.pdf --pipeline vlm --vlm-model smoldocling -o paper.md
python3 scripts/docling_convert.py paper.pdf --pipeline vlm --vlm-model granite_docling_mlx -o paper.md  # Apple Silicon
# Hybrid: deterministic text for text regions, VLM only for images/tables (less hallucination):
python3 scripts/docling_convert.py paper.pdf --pipeline vlm --force-backend-text -o paper.md
```

Remote VLM endpoints (vLLM / Ollama / LM Studio / hosted) require the Python API
for URL/model/key config — pass `--remote` to allow outbound HTTP and see
[references/pipelines.md](references/pipelines.md) and
[references/python-api.md](references/python-api.md).

### ASR pipeline (audio / video → transcript)

```bash
python3 scripts/docling_convert.py meeting.m4a --pipeline asr -o meeting.md
python3 scripts/docling_convert.py talk.mp4  --pipeline asr --asr-model whisper_small -o talk.md
```

Whisper presets: `whisper_tiny` (default) · `whisper_small` · `whisper_medium`
· `whisper_turbo`. Needs `pip install "docling[asr]"`.

### Enrichments (each pulls an extra model on first use)

```bash
python3 scripts/docling_convert.py code_manual.pdf --enrich-code -o out.md          # tag code blocks
python3 scripts/docling_convert.py math_paper.pdf  --enrich-formula -o out.md        # formulas → LaTeX
python3 scripts/docling_convert.py figures.pdf --enrich-picture-classes -o out.md    # classify figures
python3 scripts/docling_convert.py figures.pdf --enrich-picture-description --remote -o out.md  # caption figures
```

### Runtime / safety knobs

```bash
--device auto|cpu|cuda|mps    --threads N
--max-pages N                 # only the first N pages (large/untrusted inputs)
--max-file-size BYTES         # reject oversized inputs
--quiet                       # silence docling's per-page logging
```

For encrypted PDFs the CLI is most reliable:
`docling secret.pdf --pdf-password PW --output ./out/`.

---

## Part 2 — Tables & figures

**Figures / page images** — `--images` exports referenced figures. With `--to md`
it writes `report.md` plus image files; with other formats it drops PNGs into a
`figures/` folder.

```bash
python3 scripts/docling_convert.py paper.pdf --to md --images -o paper.md
python3 scripts/docling_convert.py paper.pdf --to json --images --image-dir ./assets -o paper.json
```

**Every table as CSV** — via the analyzer:

```bash
python3 scripts/docling_analyze.py report.pdf --tables-dir ./tables
```

For programmatic table access (`export_to_dataframe`, `export_to_html`,
merged-cell handling), see [references/python-api.md](references/python-api.md).

---

## Part 3 — Chunk for RAG (`docling_chunk.py`)

Produces **JSONL, one embedding-ready record per line**. The `text` field is
run through `contextualize()` so each chunk carries its heading breadcrumb —
this materially improves retrieval. Accepts a source document **or an existing
DoclingDocument `.json`** (skip re-conversion).

```bash
# Hybrid (default): heading-aware, then packed to a token budget
python3 scripts/docling_chunk.py report.pdf -o chunks.jsonl --max-tokens 512

# Reuse a prior JSON export (fast — no re-parse)
python3 scripts/docling_chunk.py report.json -o chunks.jsonl

# OpenAI embedding tokenizer
python3 scripts/docling_chunk.py report.pdf --tokenizer openai --openai-model text-embedding-3-small --max-tokens 8192 -o chunks.jsonl

# Pure structural split (no tokenizer / no budget)
python3 scripts/docling_chunk.py report.pdf --strategy hierarchical -o chunks.jsonl
```

Each record: `id`, `text` (contextualized — embed this), `raw_text`, `headings`,
`page_numbers`, `source`, `token_count`. Summary line reports chunk count and
min/max/avg tokens. Framework loaders (LangChain/LlamaIndex/Haystack) and vector
DB wiring: [references/rag-integration.md](references/rag-integration.md).

---

## Part 4 — Analyze structure (`docling_analyze.py`)

Answer "what's in this document?" **without** dumping its full content: page
count, heading tree, table/figure inventory with captions and page numbers, and
per-label item counts.

```bash
python3 scripts/docling_analyze.py report.pdf                 # JSON to stdout + human outline to stderr
python3 scripts/docling_analyze.py report.json --json-only -o structure.json
python3 scripts/docling_analyze.py report.pdf --tables-dir ./tables   # + dump every table to CSV
```

---

## Part 5 — Batch a folder (`docling_batch.py`)

One converter, models loaded once, `manifest.json` recording per-file
success/failure so a pipeline can retry only the failures.

```bash
python3 scripts/docling_batch.py ./inbox --outdir ./out --glob "*.pdf" --to md
python3 scripts/docling_batch.py ./inbox --outdir ./out --recursive --to json
```

Exit code is `1` if **any** document failed (see `manifest.json`), else `0`.

---

## Part 6 — Quality loop (`docling_evaluate.py`) — check your work

For any conversion where fidelity matters (not a quick preview), **verify, then
refine**. This is how the agent checks its own output instead of hoping.

**A. Produce JSON (and Markdown) and evaluate**

```bash
python3 scripts/docling_convert.py "<src>" --to json -o /tmp/doc.json
python3 scripts/docling_convert.py "<src>" --to md   -o /tmp/doc.md
python3 scripts/docling_evaluate.py /tmp/doc.json --markdown /tmp/doc.md
```

Add `--expect-tables` for invoices/spreadsheets; `--fail-on-warn` in CI. The
report is JSON: `status` (`pass`|`warn`|`fail`), `metrics`, `issues`, and
`recommended_actions` (concrete flags to try next).

**B. Refine (max 3 attempts unless told otherwise)**

1. If `warn`/`fail`, apply **one** change from `recommended_actions`
   (e.g. `--force-ocr`, a different `--ocr-engine`, `--accurate-tables`,
   `--pipeline vlm`).
2. Re-convert, re-evaluate.
3. Stop at `pass`, or after 3 tries — then summarize what worked and what's
   still imperfect.

**Manual checklist** if the evaluator can't run: page count roughly matches the
source; Markdown isn't near-empty; expected tables are present; no runs of `�`
replacement characters; no line repeated many times (a layout/OCR loop → try
`--pipeline vlm` or `--force-backend-text`).

---

## Offline / air-gapped

```bash
docling-tools models download                    # pre-fetch all models
export DOCLING_ARTIFACTS_PATH=/path/to/models     # point Docling at them
export OMP_NUM_THREADS=8                           # CPU thread control
```

Then run with `--device cpu`. Remote-service features (remote VLM, figure
description via API) stay disabled unless you pass `--remote`.

---

## Output conventions

- Always report page count and conversion status (the scripts print a
  `summary: {...}` line to stderr — surface its key fields).
- Markdown: render directly unless the user will copy/paste, then fence it.
- JSON: pretty-printed (`indent=2`) by default.
- Chunks: report total count and min/max/avg tokens.
- Structure: lead with the heading tree + table/figure counts before detail.
- When you ran the quality loop, state the final `status` and which attempt
  produced it.

## References

- [references/pipelines.md](references/pipelines.md) — standard / VLM / ASR, OCR engines, model presets, remote API
- [references/cli-reference.md](references/cli-reference.md) — full `docling` CLI flags
- [references/python-api.md](references/python-api.md) — verified Python recipes (tables, figures, provenance, serialization, remote VLM)
- [references/rag-integration.md](references/rag-integration.md) — LangChain / LlamaIndex / Haystack, vector DBs, MCP server
- [references/formats.md](references/formats.md) — input/output format matrix
- [references/troubleshooting.md](references/troubleshooting.md) — problem → fix
- Docling docs — https://docling-project.github.io/docling/ · CLI — https://docling-project.github.io/docling/reference/cli/
