# Pipelines, OCR engines & model presets

Docling has three processing pipelines. Pick by input type, hardware, and
latency budget.

| Pipeline | CLI | Best for | Cost |
|---|---|---|---|
| **standard** (default) | `--pipeline standard` | born-digital PDFs, Office, HTML; scans via OCR | CPU-friendly, fast |
| **vlm** | `--pipeline vlm` | complex layout, multi-column, handwriting, formulas, bad reading order | GPU/MPS preferred, slower |
| **asr** | `--pipeline asr` | audio & video → transcript | Whisper models |

There is also a `legacy` value kept for backward compatibility — do not use it
for new work.

## Decision matrix

| Document | Pipeline | Why |
|---|---|---|
| Born-digital PDF (text selectable) | standard | fast, accurate, no GPU |
| Office (DOCX/PPTX/XLSX), HTML, MD | standard | native backends, no OCR needed |
| Scanned / photographed / image-only PDF | standard + `--force-ocr`, or vlm | OCR recovers text; VLM if layout is messy |
| Multi-column / dense tables / posters | vlm | better structural understanding |
| Handwriting, formulas, figures w/ embedded text | vlm | only viable option |
| Air-gapped / CPU only | standard | runs on CPU |
| GPU server, high throughput | vlm via vLLM | best batch throughput |
| Apple Silicon / local dev | vlm via MLX | MPS acceleration |
| Audio / video recording | asr | Whisper transcription |

---

## Standard pipeline — OCR engines

OCR is enabled by default (bitmap regions only). Use `--force-ocr` to OCR every
page (full scans). Engines are plug-and-play:

| Engine | CLI flag | Install | Notes |
|---|---|---|---|
| EasyOCR | `--ocr-engine easyocr` (default) | none extra | good default |
| RapidOCR | `--ocr-engine rapidocr` | `pip install rapidocr onnxruntime` | light, no C deps |
| Tesseract (Python) | `--ocr-engine tesserocr` | `pip install tesserocr` + system tesseract | fast, accurate |
| Tesseract (CLI) | `--ocr-engine tesseract` | system `tesseract` binary | shells out |
| macOS Vision | `--ocr-engine ocrmac` | `pip install ocrmac` | macOS only |

Languages: `--ocr-lang "en+fr"` (EasyOCR/RapidOCR codes) or `"eng+deu"`
(Tesseract codes). Tesseract page-segmentation mode: `--psm N`.

Tables use TableFormer. `--table-mode accurate` (CLI) / `--accurate-tables`
(script) is slower but far better on merged-cell and borderless tables;
`--no-tables` skips detection for speed.

---

## VLM pipeline — model presets

| CLI `--vlm-model` | Python preset (`vlm_model_specs.*`) | Backend | Device |
|---|---|---|---|
| `granite_docling` (default) | `GRANITEDOCLING_TRANSFORMERS` | HF Transformers | CPU/GPU |
| `smoldocling` | `SMOLDOCLING_TRANSFORMERS` | HF Transformers | CPU/GPU (lighter) |
| `granite_docling_mlx` | `GRANITEDOCLING_MLX` | MLX | Apple MPS |
| `granite_docling_vllm` | `GRANITEDOCLING_VLLM` | vLLM | GPU (fast batch) |

Install: `pip install "docling[vlm]"` (torch + transformers + accelerate).
Apple Silicon MLX: `pip install mlx mlx-lm`.

**Hybrid mode** (`--force-backend-text`, or `force_backend_text=True` in Python):
deterministic PDF text extraction for text regions, VLM only for images/tables.
Reduces hallucination on text-heavy pages while keeping VLM quality for visuals.

### Remote VLM API (vLLM / Ollama / LM Studio / hosted)

CLI can enable it (`--pipeline vlm --enable-remote-services`) but URL, model,
and API key need the Python API (`ApiVlmOptions`). See
[python-api.md](python-api.md). `enable_remote_services=True` is **mandatory** —
Docling blocks outbound HTTP by default.

| Server | Default URL |
|---|---|
| vLLM | `http://localhost:8000/v1/chat/completions` |
| LM Studio | `http://localhost:1234/v1/chat/completions` |
| Ollama | `http://localhost:11434/v1/chat/completions` (model `ibm/granite-docling:258m`) |
| Hosted / OpenAI-compatible | provider URL + `Authorization` header |

---

## ASR pipeline — Whisper presets

| CLI `--asr-model` | Python preset (`asr_model_specs.*`) | Notes |
|---|---|---|
| `whisper_tiny` (default) | `WHISPER_TINY` | fastest, lowest accuracy |
| `whisper_small` | `WHISPER_SMALL` | good balance |
| `whisper_medium` | `WHISPER_MEDIUM` | higher accuracy |
| `whisper_turbo` | `WHISPER_TURBO` | fast + accurate |

Install: `pip install "docling[asr]"`. Accepts wav/mp3/m4a/aac/ogg/flac and
mp4/avi/mov (audio track). Output is a transcript document you can export like
any other (`--to md`, `--to json`, `--to vtt` via the CLI).
