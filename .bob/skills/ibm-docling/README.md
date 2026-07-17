# ibm-docling

A **production-grade [Docling](https://github.com/docling-project/docling)
Agent Skill** for **Bob**. It gives the agent one coherent, verified surface 
for every Docling use case: convert any document to Markdown/JSON/HTML/DocTags, 
OCR scans, run vision-language (VLM) or speech (ASR) pipelines, extract tables 
and figures, apply enrichments, chunk for RAG, analyze structure, batch-process 
directories, and self-check output quality.

It is built the same way as `pdf-toolkit`: **deterministic CLI scripts with
graceful degradation and clean exit codes**, backed by a verified library and
CLI reference so the agent never guesses the API.

## Layout

```
SKILL.md              # the agent's operating manual — decision guide + every workflow
requirements.txt      # tiered dependencies (install only what a task needs)
scripts/
  docling_convert.py  # workhorse: any input -> md/text/json/yaml/html/doctags
  docling_chunk.py    # RAG chunking -> JSONL (hybrid/hierarchical, HF/OpenAI tokenizers)
  docling_analyze.py  # structure report: headings, tables, figures, per-page stats
  docling_batch.py    # batch a directory -> outputs + manifest.json
  docling_evaluate.py # heuristic quality gate + "try this next" recommendations
  selftest.sh         # verify the whole install in one command
references/
  pipelines.md        # standard vs VLM vs ASR; OCR engines; model presets; remote API
  cli-reference.md    # full `docling` CLI flag reference
  python-api.md       # verified Python recipes (tables, figures, provenance, serialization)
  rag-integration.md  # LangChain / LlamaIndex / Haystack + vector DBs + MCP server
  formats.md          # supported input/output format matrix
  troubleshooting.md  # problem -> fix table
```

## Quick start

```bash
pip install -r requirements.txt          # tier 1: convert + OCR + tables + chunk
bash scripts/selftest.sh                  # verify end to end

# convert
python3 scripts/docling_convert.py report.pdf --to md -o report.md
docling report.pdf --output ./out/        # equivalent one-off via the CLI

# scanned PDF, better tables
python3 scripts/docling_convert.py scan.pdf --force-ocr --accurate-tables -o scan.md

# complex layout / handwriting / formulas -> VLM
python3 scripts/docling_convert.py paper.pdf --pipeline vlm -o paper.md

# audio/video transcription -> VLM's ASR sibling
python3 scripts/docling_convert.py meeting.m4a --pipeline asr -o meeting.md

# RAG
python3 scripts/docling_chunk.py report.pdf -o chunks.jsonl --max-tokens 512

# check the work
python3 scripts/docling_convert.py report.pdf --to json -o report.json
python3 scripts/docling_evaluate.py report.json --markdown report.md
```

## Dependency tiers

| Tier | Install | Enables |
|---|---|---|
| 1 core | `pip install -r requirements.txt` | convert, OCR (EasyOCR), tables, structure, chunking — CPU only |
| 2 VLM | `pip install "docling[vlm]"` | GraniteDocling/SmolDocling local vision pipeline |
| 3 MLX | `pip install mlx mlx-lm` | Apple-Silicon acceleration for VLM |
| 4 ASR | `pip install "docling[asr]"` | audio/video transcription (Whisper) |
| 5 RAG | `pip install "docling-core[chunking-openai]" langchain-docling` | OpenAI tokenizer, framework loaders |
| 6 OCR | `pip install rapidocr tesserocr ocrmac` | alternate OCR engines |

Every script exits `0` on success, `1` on a runtime/usage error, and `2` when a
required dependency is missing (with the exact `pip install` to run). Scripts and
the `docling` CLI are interchangeable for conversion; the scripts add figure
extraction, a machine-readable summary, and automation-friendly exit codes.

## License

MIT - aligned with [Docling](https://github.com/docling-project/docling). The
evaluator is adapted from Docling's own agent-skill example (MIT).
