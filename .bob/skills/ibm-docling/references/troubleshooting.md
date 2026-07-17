# Troubleshooting

Exit codes across the skill scripts: **`0`** ok · **`1`** runtime/usage error ·
**`2`** missing dependency (the message prints the exact `pip install`).

| Problem | Fix |
|---|---|
| `docling is not installed` (exit 2) | `pip install docling docling-core` |
| Conversion output is empty / near-empty | Scanned PDF — add `--force-ocr`; if still poor, `--pipeline vlm` |
| Low text density flagged by the evaluator | `--force-ocr` with a different `--ocr-engine`, or `--pipeline vlm` |
| `�` replacement characters in text | Wrong OCR result — try `--ocr-engine tesseract` (or `rapidocr`), or VLM |
| Same line repeated many times | Layout/OCR loop — `--pipeline vlm`, or `--force-backend-text` (hybrid) |
| Tables missing / wrong structure | Ensure tables on (no `--no-tables`), add `--accurate-tables`; VLM for merged cells |
| Wrong reading order (multi-column) | `--pipeline vlm` — standard may interleave columns |
| Handwriting / formulas not captured | `--pipeline vlm` only; add `--enrich-formula` for LaTeX |
| VLM hallucinating text on text-heavy pages | `--force-backend-text` (deterministic text + VLM for visuals) |
| VLM API call blocked / no HTTP | Pass `--remote` (script) or `--enable-remote-services` (CLI); remote is off by default |
| Remote VLM URL/model/key won't set via CLI | Only the Python API configures these — see `python-api.md` |
| Encrypted PDF error | Use the CLI: `docling secret.pdf --pdf-password 'PW' --output ./out/` |
| Models fail to download | `docling-tools models download`; set `DOCLING_ARTIFACTS_PATH` for air-gapped |
| Docling OOM on a big PDF | `--max-pages N` and/or `--max-file-size BYTES`; process in batches |
| Slow on born-digital PDFs | `--no-ocr` (skip OCR) and default `fast` table mode |
| Apple Silicon, want acceleration | `--pipeline vlm --vlm-model granite_docling_mlx` (needs `mlx mlx-lm`), or `--device mps` |
| CUDA not used | `--device cuda`; verify `torch.cuda.is_available()` |
| ASR: `docling[asr]` not installed | `pip install "docling[asr]"` |
| OpenAI tokenizer chunking fails | `pip install 'docling-core[chunking-openai]'` (needs tiktoken) |
| First chunk run stalls | It's downloading the HuggingFace tokenizer once; subsequent runs are fast |
| `AttributeError: 'PdfPipelineOptions' object has no attribute 'backend'` | You used `format_options={"pdf": opts}` — use `InputFormat.PDF` + `PdfFormatOption` (see `python-api.md`) |
| `table.to_markdown()` fails | It's `table.export_to_markdown(doc=doc)` |
| `export_to_dataframe()` TypeError on `doc=` | Older docling — call `export_to_dataframe()` without the kwarg (the scripts already fall back) |
| Need to re-run analysis/chunk/eval cheaply | Convert once with `--to json`, then point the other scripts at the `.json` |
| Want to see what Docling detected | `docling <src> --debug-visualize-layout --debug-visualize-tables --output ./out/` |

## Verifying an install

```bash
bash scripts/selftest.sh
```

It checks the CLI and imports, synthesizes a sample PDF, then exercises
convert → analyze → evaluate → chunk. Any `FAIL` line names the missing piece.

## When to escalate pipelines

1. **standard** (fast, CPU) — try first for anything born-digital.
2. **standard + `--force-ocr`** — for scans/photos.
3. **standard + `--accurate-tables`** — when tables are the point.
4. **vlm** — complex layout, handwriting, formulas, or when 1–3 score `warn`/`fail`.
5. **vlm + `--force-backend-text`** — VLM quality on visuals without text hallucination.

Drive these transitions with `docling_evaluate.py` rather than guessing — its
`recommended_actions` name the exact next flag to try.
