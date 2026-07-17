---
name: pptx-ibm-template
description: >-
  Use this skill any time a .pptx file is involved in any way — as input,
  output, or both. This includes: creating slide decks, pitch decks, or
  presentations; reading, parsing, or extracting text from any .pptx file
  (even if the extracted content will be used elsewhere, like in an email or
  summary); editing, modifying, or updating existing presentations; combining
  or splitting slide files; working with templates, layouts, speaker notes, or
  comments. Trigger whenever the user mentions "deck," "slides,"
  "presentation," or references a .pptx filename, regardless of what they plan
  to do with the content afterward. If a .pptx file needs to be opened,
  created, or touched, use this skill.
license: Proprietary. LICENSE.txt has complete terms
metadata:
  enabled: true
---

# PPTX Skill — Read · Edit · Create · IBM-Branded Presentations

End-to-end guide for working with PowerPoint files: reading content, editing
existing presentations from templates, creating from scratch with PptxGenJS,
and producing IBM-branded decks from the official IBM Carbon template.

> **Golden rule — IBM presentations:** the IBM template ships a complete slide
> master, fonts, logo, cover imagery, and 48 named layouts. **NEVER create IBM
> presentations with PptxGenJS** — it produces a blank canvas that loses all of
> this. Always use the template workflow in
> [references/ibm-template.md](references/ibm-template.md).

---

## 1. Mental model — four paths

| Goal | Approach | Reference |
|------|----------|-----------|
| Extract / read text from a .pptx | `markitdown` | §2 |
| Edit an existing presentation or use a template | Unpack → edit XML → clean → pack | [references/editing.md](references/editing.md) |
| Create from scratch (non-IBM) | PptxGenJS | [references/pptxgenjs.md](references/pptxgenjs.md) |
| **IBM-branded presentation** | Copy IBM template → unpack → edit XML → pack — ⛔ NEVER PptxGenJS | [references/ibm-template.md](references/ibm-template.md) |

Scripts live in `references/scripts/`. The IBM template is bundled at `references/assets/ibm-template.pptx`.

---

## 2. Reading content

```bash
# Text extraction (.pptx only)
python -m markitdown presentation.pptx

# Visual overview (grid of slide thumbnails)
python references/scripts/thumbnail.py presentation.pptx

# Raw XML inspection
python references/scripts/office/unpack.py presentation.pptx unpacked/
```

---

## 3. Editing or template-based workflow

**Read [references/editing.md](references/editing.md) for full details.**

The core loop:

```bash
python references/scripts/office/unpack.py input.pptx unpacked/
# … edit unpacked/ppt/slides/slideN.xml …
python references/scripts/clean.py unpacked/
python references/scripts/office/pack.py unpacked/ output.pptx --original input.pptx
```

Helper scripts:

| Script | Purpose |
|--------|---------|
| `references/scripts/office/unpack.py` | Extract + pretty-print XML |
| `references/scripts/add_slide.py` | Duplicate a slide or create from a layout |
| `references/scripts/clean.py` | Remove orphaned slides, media, rels |
| `references/scripts/office/pack.py` | Repack with validation |
| `references/scripts/thumbnail.py` | Thumbnail grid for template analysis |

---

## 4. Creating from scratch (non-IBM only)

**Read [references/pptxgenjs.md](references/pptxgenjs.md) for full details.**

Use PptxGenJS only when there is no template or reference presentation. Never
for IBM-branded slides — see §5.

```bash
npm install -g pptxgenjs
node create_presentation.js
```

Key PptxGenJS rules (from [references/pptxgenjs.md](references/pptxgenjs.md)):
- Never prefix hex colors with `#` — corrupts the file
- Never encode opacity in 8-char hex strings — use the `opacity` property
- Never reuse option objects across `addShape`/`addText` calls — PptxGenJS mutates them in-place

---

## 5. IBM-branded presentations

> **⛔ MANDATORY: Use the template workflow. NEVER use PptxGenJS for IBM slides.**
> PptxGenJS creates a blank canvas — the IBM slide master, logo, fonts, cover
> imagery, footer branding, and all visual assets will be missing. The template
> carries all of this automatically.

**Read [references/ibm-template.md](references/ibm-template.md) before doing anything else.**

The template is at `references/assets/ibm-template.pptx`. Quick workflow:

```bash
cp references/assets/ibm-template.pptx output.pptx
python references/scripts/office/unpack.py output.pptx unpacked/
# … add/edit slides …
python references/scripts/clean.py unpacked/
python references/scripts/office/pack.py unpacked/ output.pptx --original references/assets/ibm-template.pptx
```

IBM Carbon design tokens at a glance:

| Token | Value | Used for |
|-------|-------|----------|
| IBM Blue 60 | `0F62FE` | Accent bars, divider lines, CTAs |
| IBM Blue 90 (dark navy) | `003A6D` | Dark backgrounds, section headers |
| IBM Cyan 10 | `E5F6FF` | Cyan cover variant background |
| White | `FFFFFF` | Content slide backgrounds |
| Font | IBM Plex Sans Light | All text — no bold, no mixed fonts |

48 named layouts — covers, section dividers, stat callouts, text columns, box
grids, media, utility slides. Full layout catalog and design rules are in
[references/ibm-template.md](references/ibm-template.md).

**Template imagery:** IBM logo, cover photos, and decorative assets are embedded
in the template master. They appear automatically when using the template
workflow. See the *Template Media & Images* section in
[references/ibm-template.md](references/ibm-template.md) for how they carry
through and how to replace cover photos.

---

## 6. Design principles

**Don't create boring slides.** Plain bullets on a white background won't impress anyone.

### Before starting

- **Bold, content-informed palette**: colors should feel designed for *this* topic — not interchangeable with any other presentation.
- **Dominance over equality**: one color at 60–70% visual weight, 1–2 supporting tones, one sharp accent.
- **Dark/light contrast**: dark covers + light content slides ("sandwich"), or commit to dark throughout.
- **One visual motif, repeated**: rounded frames, icons in colored circles, thick single-side borders — pick one and carry it.

### Layout options (vary across slides)

- Two-column (text left, illustration right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2×2 or 2×3 grid
- Half-bleed image with content overlay
- Large stat callouts (60–72pt numbers with small labels)
- Timeline or process flow (numbered steps, arrows)

### Typography

| Element | Size |
|---------|------|
| Slide title | 36–44pt |
| Section header | 20–24pt |
| Body text | 14–16pt |
| Captions | 10–12pt |

IBM presentations: IBM Plex Sans Light for all text. Non-IBM presentations: pick a pairing with personality (see [references/pptxgenjs.md](references/pptxgenjs.md) for options).

### Avoid

- Repeating the same layout across all slides
- Center-aligning body text (left-align paragraphs and lists; center only titles)
- Text-only slides — every slide needs an image, chart, icon, or shape
- Accent lines under titles — use whitespace or background color instead
- Low-contrast elements (light text on light backgrounds, dark icons on dark backgrounds)
- Mixing spacing randomly — pick 0.3" or 0.5" gaps and use them consistently

---

## 7. QA (required)

**Assume there are problems. Your job is to find them.**

Your first render is almost never correct. Treat QA as a bug hunt, not confirmation.

### Content QA

```bash
python -m markitdown output.pptx

# Check for leftover placeholder text
python -m markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout|firstname|lastname|click to edit"
```

### Visual QA

**Use subagents** — even for 2–3 slides. Convert to images first (§8), then
pass the absolute image paths to a subagent with this prompt:

```
Visually inspect these slides. Assume there are issues — find them.

Look for: overlapping elements, text overflow, decorative lines misaligned with
wrapped titles, source citations colliding with content, elements too close
(< 0.3" gaps), uneven gaps, insufficient margins (< 0.5"), misaligned columns,
low-contrast text or icons, text boxes too narrow, leftover placeholder content.

For each slide, list issues or areas of concern, even if minor.

Read and analyze these images:
1. <absolute-path>/slide-N.jpg — (Expected: [brief description])
...
```

### Verification loop

1. Generate → convert to images → inspect
2. List issues (if none found, look again more critically)
3. Fix issues
4. Re-verify affected slides — one fix often creates another problem
5. Repeat until a full pass finds no new issues

**Do not declare success until you've completed at least one fix-and-verify cycle.**

---

## 8. Converting to images

```bash
python references/scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

Pass the printed absolute paths directly to the view tool. `pdftoppm` zero-pads
based on page count: `slide-1.jpg` for decks under 10 pages, `slide-01.jpg` for
10–99. **After fixes, rerun all four commands** — the PDF must be regenerated
before `pdftoppm` reflects your changes.

---

## 9. References (load on demand)

| File | Contents |
|------|----------|
| [references/editing.md](references/editing.md) | Template-based workflow, slide operations (add/delete/reorder), editing content in XML, formatting rules, common pitfalls |
| [references/pptxgenjs.md](references/pptxgenjs.md) | Full PptxGenJS tutorial: text, shapes, images, icons, tables, charts, slide masters, common pitfalls |
| [references/ibm-template.md](references/ibm-template.md) | IBM Carbon design system, color palette, typography, all 48 named layouts, IBM design rules, template media/images, full workflow |

---

## 10. Dependencies

```bash
pip install "markitdown[pptx]"   # text extraction
pip install Pillow                # thumbnail grids
npm install -g pptxgenjs          # creating from scratch (non-IBM only)
# LibreOffice (soffice) — PDF conversion, auto-configured via references/scripts/office/soffice.py
# Poppler (pdftoppm) — PDF to images
```
