# pdf-toolkit

A swiss-army-knife Skill for Bob working with PDFs end to end. It **reads and parses**
PDFs (text, tables, figures, OCR → Markdown/JSON/CSV), **manipulates** them
(merge, split, rotate, watermark, encrypt/decrypt, edit metadata, extract images,
compress, list/fill forms), and **generates** new themed PDFs from Markdown. It is
built around three deterministic CLI scripts with graceful fallback, so common
tasks work even when the heavy dependencies aren't installed.

## Layout

```
SKILL.md            # full instructions + verified library reference
requirements.txt    # tiered Python dependencies
scripts/            # pdf_ops.py · extract.py · generate_pdf.py · fix_markdown.py
references/          # Pandoc quick-reference + YAML frontmatter templates
```

## Dependencies (tiered — install only what you need)

| Tier | Install | Enables |
|---|---|---|
| 1 — manipulation + fast extraction | `pip install pypdf pikepdf pdfplumber` | all of `pdf_ops.py`; basic `extract.py` (no OCR) |
| 2 — pure-python generation | `pip install reportlab markdown` (or `weasyprint`) | LaTeX-free PDF generation |
| 3 — high-fidelity read (heavy, ML) | `pip install "docling>=2.0"` | layout, tables, OCR, figures, RAG |
| Gen — best-quality generation | `brew install pandoc && brew install --cask mactex` | themed PDFs via `generate_pdf.py` |

Baseline (tiers 1+2): `pip install -r requirements.txt`. Tier 3 and the Pandoc
toolchain are optional and installed separately. See `SKILL.md` for full usage.
