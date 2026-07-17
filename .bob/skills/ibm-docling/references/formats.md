# Supported formats

## Input formats

Docling auto-detects format by extension / MIME / content. Pass `--from` to
constrain it.

| Family | Extensions | Pipeline |
|---|---|---|
| PDF | `pdf` | standard / vlm |
| Word | `docx dotx docm dotm` | standard (native backend) |
| PowerPoint | `pptx potx ppsx pptm potm ppsm` | standard |
| Excel | `xlsx xlsm` | standard |
| HTML | `html htm xhtml` | standard |
| Markdown / text | `md txt text qmd rmd Rmd` | standard |
| AsciiDoc | `adoc asciidoc asc` | standard |
| CSV | `csv` | standard |
| Images | `png jpg jpeg tif tiff bmp webp` | standard (OCR) / vlm |
| XML (scientific) | `xml nxml` (JATS), USPTO patents, XBRL | standard |
| DocLang | `dclg dclg.xml` | standard |
| DoclingDocument JSON | `json` (a prior export) | re-load, no re-parse |
| Audio / video | `wav mp3 m4a aac ogg flac mp4 avi mov` | **asr** |

A **URL** to any of the above works anywhere a path does.

> The skill scripts converge PDF and IMAGE onto the PDF-style pipeline options
> (OCR, tables, enrichments). Office/HTML/MD/CSV use their native backends and
> ignore OCR/table flags.

## Output formats

| `--to` | What you get | Best for |
|---|---|---|
| `md` (default) | GitHub-flavored Markdown | LLM input, human review |
| `text` | plain text, no markup | search, simple ingestion |
| `json` | lossless `DoclingDocument` (bbox, hierarchy, provenance, confidence) | downstream processing, re-load, evaluation |
| `yaml` | same structure as JSON, YAML-encoded | human-diffable structured export |
| `html` | standalone HTML (embed or reference images) | previews, reports |
| `doctags` | DocTags serialization (VLM-native token format) | VLM round-trips, training data |
| `vtt` (CLI) | subtitles/transcript with timings | ASR output |
| `chunks` (CLI) | chunk stream | quick RAG preview (prefer `docling_chunk.py` for JSONL) |

### Which output should I pick?

- **Human wants to read it** → `md`.
- **You'll process it further, evaluate it, or chunk it later** → `json` (it's
  lossless and re-loadable by every skill script without re-parsing).
- **Feeding another VLM / building training data** → `doctags`.
- **Transcribing audio/video for captions** → `vtt` (via the CLI).

The lossless `json` export is the recommended intermediate: convert once to
JSON, then run `docling_analyze.py`, `docling_chunk.py`, and `docling_evaluate.py`
against it without paying for conversion again.
