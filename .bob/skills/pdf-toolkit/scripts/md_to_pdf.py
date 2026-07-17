#!/usr/bin/env python3
"""
md_to_pdf.py — pure-python Markdown -> PDF (no LaTeX / system libs).

A lightweight generation fallback for when Pandoc/XeLaTeX and WeasyPrint aren't
available. Uses only reportlab. Supports headings (#..####), paragraphs,
bullet/numbered lists, code fences, blockquotes, horizontal rules, and inline
**bold** / *italic* / `code`. Optional YAML front matter drives the title block.

Usage:
  python3 md_to_pdf.py input.md -o output.pdf
  python3 md_to_pdf.py input.md -o output.pdf --title "Report" --accent 0f62fe

Exit codes: 0 ok, 1 runtime error, 2 missing dependency (reportlab).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _need_reportlab():
    try:
        import reportlab  # noqa: F401
    except ImportError:
        sys.stderr.write("error: reportlab required. pip install reportlab\n")
        sys.exit(2)


def _split_frontmatter(text: str):
    """Return (meta dict, body). Parses a leading --- ... --- YAML-ish block."""
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            block = text[3:end].strip("\n")
            body = text[end + 4:].lstrip("\n")
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            return meta, body
    return meta, text


def _inline(text: str) -> str:
    """Minimal inline Markdown -> reportlab mini-HTML, escaping first."""
    text = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<link href="\2"><u>\1</u></link>', text)
    return text


def build(md_text: str, out_path: str, title=None, accent="0f62fe"):
    _need_reportlab()
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        HRFlowable, Paragraph, Preformatted, SimpleDocTemplate, Spacer,
    )

    meta, body = _split_frontmatter(md_text)
    accent_c = HexColor("#" + accent.lstrip("#"))
    styles = getSampleStyleSheet()
    h_styles = {
        1: ParagraphStyle("H1", parent=styles["Heading1"], textColor=accent_c,
                          spaceBefore=14, spaceAfter=6),
        2: ParagraphStyle("H2", parent=styles["Heading2"], textColor=accent_c,
                          spaceBefore=12, spaceAfter=4),
        3: ParagraphStyle("H3", parent=styles["Heading3"], spaceBefore=10),
        4: ParagraphStyle("H4", parent=styles["Heading4"], spaceBefore=8),
    }
    body_style = ParagraphStyle("Body", parent=styles["BodyText"], alignment=TA_LEFT,
                                leading=15, spaceAfter=6)
    quote_style = ParagraphStyle("Quote", parent=body_style, leftIndent=16,
                                 textColor=HexColor("#525252"), borderPadding=4)
    code_style = ParagraphStyle("Code", parent=styles["Code"], fontSize=8,
                                backColor=HexColor("#f4f4f4"), leading=10)
    # Hanging-indent list style. We render the bullet/number as normal text (a
    # real "•" U+2022 in the body font) rather than reportlab's symbol-font
    # ListFlowable bullet, so the generated PDF's text layer stays clean and
    # extractable (no (cid:127) artifacts).
    li_style = ParagraphStyle("ListItem", parent=body_style, leftIndent=18,
                              firstLineIndent=-12, spaceAfter=2)

    flow = []
    # Title block
    disp_title = title or meta.get("title")
    if disp_title:
        flow.append(Paragraph(_inline(disp_title),
                              ParagraphStyle("Title", parent=styles["Title"],
                                             textColor=accent_c)))
        for key in ("subtitle", "author", "date"):
            if meta.get(key):
                flow.append(Paragraph(_inline(meta[key]), body_style))
        flow.append(HRFlowable(width="100%", color=accent_c, thickness=1.5,
                               spaceBefore=6, spaceAfter=12))

    lines = body.splitlines()
    i = 0
    pending_list = []      # (ordered: bool, [items])
    list_ordered = False

    def flush_list():
        nonlocal pending_list, list_ordered
        if pending_list:
            for idx, t in enumerate(pending_list, 1):
                # ASCII marker keeps the generated text layer clean; reportlab's
                # standard fonts have no ToUnicode entry for "•", which would
                # re-extract as (cid:127).
                marker = f"{idx}." if list_ordered else "-"
                flow.append(Paragraph(f"{marker}&nbsp;&nbsp;{_inline(t)}", li_style))
            flow.append(Spacer(1, 4))
            pending_list = []

    para_buf = []

    def flush_para():
        if para_buf:
            flow.append(Paragraph(_inline(" ".join(para_buf)), body_style))
            para_buf.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):            # code fence
            flush_para(); flush_list()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            flow.append(Preformatted("\n".join(code) or " ", code_style))
            flow.append(Spacer(1, 6))
            i += 1
            continue

        if not stripped:                           # blank line
            flush_para(); flush_list()
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)", stripped)
        if m:
            flush_para(); flush_list()
            lvl = len(m.group(1))
            flow.append(Paragraph(_inline(m.group(2)), h_styles[lvl]))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):   # hr
            flush_para(); flush_list()
            flow.append(HRFlowable(width="100%", color=HexColor("#c6c6c6"),
                                   spaceBefore=6, spaceAfter=6))
            i += 1
            continue

        if stripped.startswith(">"):               # blockquote
            flush_para(); flush_list()
            flow.append(Paragraph(_inline(stripped.lstrip("> ").strip()), quote_style))
            i += 1
            continue

        mb = re.match(r"^\s*([-*+])\s+(.*)", line)
        mo = re.match(r"^\s*(\d+)\.\s+(.*)", line)
        if mb or mo:
            flush_para()
            ordered = bool(mo)
            if pending_list and ordered != list_ordered:
                flush_list()
            list_ordered = ordered
            pending_list.append((mo or mb).group(2))
            i += 1
            continue

        para_buf.append(stripped)                  # normal text
        i += 1

    flush_para(); flush_list()

    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title=disp_title or "")
    doc.build(flow)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="md_to_pdf.py",
                                description="Pure-python Markdown -> PDF (reportlab).")
    p.add_argument("input", help="input Markdown file")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--title", help="override/supply document title")
    p.add_argument("--accent", default="0f62fe", help="hex accent color (default IBM Blue)")
    args = p.parse_args(argv)
    if not Path(args.input).is_file():
        sys.stderr.write(f"error: input not found: {args.input}\n")
        return 1
    try:
        build(Path(args.input).read_text(encoding="utf-8"), args.output,
              title=args.title, accent=args.accent)
        print(f"OK: wrote {args.output}")
        return 0
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"error: {type(e).__name__}: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
