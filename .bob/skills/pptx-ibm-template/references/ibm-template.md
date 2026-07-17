# IBM Template Guide

Use this guide **only** when the user explicitly asks for an IBM-branded or IBM-style presentation. Never apply it by default.

> **⛔ MANDATORY: Always use the template workflow below. NEVER create IBM slides from scratch with PptxGenJS.**
> PptxGenJS creates a blank canvas with no slide master — the IBM logo, fonts, cover imagery, footer branding, and all visual assets will be missing. The template carries all of this automatically.

## Template File

The template is bundled with this skill: **`assets/ibm-template.pptx`** (path relative to the skill root). All commands below assume this path.

Use it as the base via the editing workflow in [editing.md](editing.md) (same `references/` folder). Do **not** create IBM slides from scratch with PptxGenJS — the template has the correct fonts, master layouts, and IBM design details pre-wired.

Notes on the bundled copy:
- Sample imagery inside it was compressed to keep the skill small. Layouts, masters, fonts, and all 94 sample slides are intact.
- The embedded photos are placeholders — replace them with real assets in final decks; never ship them as-is.

---

## Template Media & Images

The IBM template embeds visual assets in `ppt/media/`. These are automatically carried into your output when you follow the template workflow.

**What's included:**
- IBM logo and wordmark (appears on the slide master — inherited by all slides automatically)
- Cover background photos (full-bleed imagery for `slideLayout1.xml`, `slideLayout5.xml`, etc.)
- Decorative pictograms and icons used by certain layouts
- Section divider background imagery

**How they carry through:**
1. When you `cp references/assets/ibm-template.pptx output.pptx` and then `unpack.py`, all media files land in `unpacked/ppt/media/`
2. Slide XML files reference media via relationship IDs (e.g., `r:embed="rId2"`) — do **not** delete or renumber these references
3. `pack.py unpacked/ output.pptx --original references/assets/ibm-template.pptx` restores any media that was pruned during unpacking

**Replacing cover photos:**
If you add a cover slide with imagery (`slideLayout1.xml` or `slideLayout5.xml`), you can either:
- Keep the placeholder photo as-is (acceptable for demos; note it as a placeholder in your QA)
- Replace it by copying a new image into `unpacked/ppt/media/`, updating the relationship in `unpacked/ppt/slides/_rels/slideN.xml.rels` to point to it, and adding it to `[Content_Types].xml`

**Do not remove unused media manually** — run `clean.py` to handle orphaned files safely. Never delete `ppt/media/` files by hand, as some are referenced from the slide master (not individual slides) and `clean.py` accounts for this.

---

## IBM Carbon Design System

### Color Palette

| Role | Name | Hex |
|------|------|-----|
| **Primary (IBM Blue 60)** | Interactive / accent bars / CTAs | `0F62FE` |
| **Dark Navy (IBM Blue 90)** | Dark backgrounds, section headers | `003A6D` |
| **IBM Purple 50** | Secondary accent | `A56EFF` |
| **IBM Teal 50** | Secondary accent | `009D9A` |
| **IBM Magenta 70** | Highlight accent | `9F1853` |
| **IBM Red 40** | Warning / alert accent | `FA4D56` |
| **IBM Cyan 10** | Light cover background | `E5F6FF` |
| **Black** | Body text on light slides | `000000` |
| **White** | Text on dark slides | `FFFFFF` |
| **Gray 50** | Muted text, visited links | `6F6F6F` |

**Color usage rules:**
- Content slides: white background (`FFFFFF`), black text (`000000`)
- Cover slides with imagery: black/dark image overlay background
- Cover "cyan" variant: `E5F6FF` background
- IBM Blue (`0F62FE`) for accent bars, thin divider lines above stat callouts, and CTAs
- Never mix more than 2 accent colors on a single slide

### Typography

**Font: IBM Plex Sans Light** — used for all text (titles, body, captions).

IBM Plex Sans is a free font available at [fonts.google.com/specimen/IBM+Plex+Sans](https://fonts.google.com/specimen/IBM+Plex+Sans). Install before creating or editing presentations.

| Element | Size | Weight |
|---------|------|--------|
| Cover title | 64pt | Light |
| Section divider title | 48–60pt | Light |
| Slide title | 36–44pt | Light |
| Stat callout (number) | 44pt | Light |
| Stat label | 24pt | Light |
| Body / bullets | 18–20pt | Light |
| Label / caption / footer | 14–16pt | Light |

IBM Plex Sans Light is thin — do not use bold except for emphasis on specific inline labels.

---

## Slide Dimensions

The IBM template uses **26.67" × 15.00"** (2× the PptxGenJS `LAYOUT_WIDE` scale). When editing XML directly, use these native coordinates.

**Grid in IBM native units (26.67" wide × 15.00" tall):**

| Element | x | y | Notes |
|---------|---|---|-------|
| Left margin | 0.63" | — | All titles and body start here |
| Title | 0.63" | 0.34–0.63" | Top of slide |
| Body content | 0.63" | 3.5–4.0" | Below title |
| Footer text | 0.63" | 14.02" | Bottom left |
| Slide number | 25.75" | 14.16" | Bottom right |
| 3-col: col 1 | 7.29" | varies | Right-side columns |
| 3-col: col 2 | 13.96" | varies | |
| 3-col: col 3 | 20.62" | varies | |

---

## Named Slide Layouts

The IBM template contains 48 named layouts. Reference these by name when planning slide mapping in the editing workflow.

### Cover Slides
| Layout | File | Background |
|--------|------|------------|
| Cover, imagery | slideLayout1.xml | Full-bleed photo |
| Cover, cyan | slideLayout2.xml | `E5F6FF` (IBM Cyan 10) |
| Cover, plain | slideLayout3.xml | White |
| Cover, plain, label | slideLayout4.xml | White + quarter/year label |
| Cover, imagery, half | slideLayout5.xml | Photo fills left half |
| Cover, imagery, half, label | slideLayout6.xml | Photo left + label |

### Navigation & Dividers
| Layout | File |
|--------|------|
| Contents | slideLayout7.xml |
| Section divider | slideLayout8.xml |
| Large text | slideLayout9.xml |

### Callout Slides (stat callouts with IBM Blue divider lines)
| Layout | File |
|--------|------|
| Callout, headline | slideLayout10.xml |
| Callout, stand-alone | slideLayout11.xml |
| Data, 2 callouts, vertical | slideLayout12.xml |
| Data, 3 callouts, vertical | slideLayout13.xml |
| Data, 2 callouts, horizontal | slideLayout14.xml |
| Data, 3 callouts, horizontal | slideLayout15.xml |

### Text Column Layouts
| Layout | File |
|--------|------|
| Text, 4 columns | slideLayout16.xml |
| Text, 4 columns, short dividers | slideLayout17.xml |
| Text, 4 columns, dividers, headlines | slideLayout18.xml |
| Text, 4 columns, dividers, pictograms | slideLayout19.xml |
| Text, 1 wide column, divider | slideLayout20.xml |
| Text, 2 wide columns | slideLayout21.xml |
| Text, 2 columns, large title | slideLayout22.xml |
| Text, 2 columns, small title | slideLayout23.xml |
| Text, 2 columns, dividers, large title | slideLayout24.xml |
| Text, 2 columns, dividers, small title | slideLayout25.xml |
| Text, 2 columns, dividers, pictograms | slideLayout26.xml |

### Box / Card Layouts
| Layout | File |
|--------|------|
| Boxes, 4 stacked wide, pictograms | slideLayout27.xml |
| Boxes, 4 stacked, small title | slideLayout28.xml |
| Boxes, 4 stacked, large title | slideLayout29.xml |
| Boxes, 4 horizontal, small title | slideLayout30.xml |
| Boxes, 4 horizontal, large title | slideLayout31.xml |
| Boxes, 6 stacked | slideLayout32.xml |
| Boxes, 6 stacked, icons | slideLayout33.xml |
| Boxes, 6 stacked, alternate, large title | slideLayout34.xml |
| Boxes, 6 stacked, alternate, small title | slideLayout35.xml |

### Media Layouts
| Layout | File |
|--------|------|
| Video or imagery, half, inset | slideLayout36.xml |
| Video or imagery, 3/4, bleed | slideLayout37.xml |
| Video or imagery, 3/4, inset | slideLayout38.xml |
| Video or imagery, bleed | slideLayout39.xml |
| Video or imagery, inset | slideLayout40.xml |

### Utility Layouts
| Layout | File |
|--------|------|
| Contacts, profiles, contributors | slideLayout41.xml |
| Table | slideLayout42.xml |
| Chart | slideLayout43.xml |
| Legal disclaimer, one column | slideLayout44.xml |
| Legal disclaimer, two columns | slideLayout45.xml |
| Blank slide | slideLayout46.xml |
| Blank slide, no footer | slideLayout47.xml |
| End slide | slideLayout48.xml |

---

## IBM Design Rules

### Structure
- **Opening**: Cover slide (imagery or cyan variant) → Contents → Section dividers → Content → End slide
- **Section dividers**: Use `slideLayout8.xml`. These are dark-background breaks between major sections.
- **End slide**: Use `slideLayout48.xml`. Never end on a content slide.
- **Footer**: Every content slide should have footer text (left, x=0.63") and slide number (right, x=25.75"). The footer typically reads: `[Topic] | [Confidentiality label]`

### Stat Callouts (the IBM signature element)
The IBM template uses a distinctive stat pattern: a thin IBM Blue line (`0F62FE`) sits above each stat, followed by a large number (44pt) and a smaller description (24pt).

```
────────────────  ← thin IBM Blue line (#0F62FE)
↓30%
Average reduction
in staff time per hire
```

Use `slideLayout12.xml`–`slideLayout15.xml` for these. When recreating in XML, place a `<p:cxnSp>` line shape with `lnW="12700"` (1pt) in IBM Blue above each stat block.

### Typography Rules
- IBM Plex Sans Light only — no mixing with other fonts
- Titles are NOT bold in IBM style (unlike most templates) — the font's thinness IS the design
- Use weight contrast through **size** not bold: big title vs. small body
- All body text left-aligned; section headers left-aligned
- Do NOT underline or bold slide titles

### What IBM Does NOT Do
- No decorative lines under titles (IBM uses whitespace instead)
- No rounded corners on content boxes (IBM uses sharp rectangular edges)
- No gradient fills on shapes (flat color only)
- No drop shadows on text
- No mixed color backgrounds on content slides (white only)
- No bullet point symbols — use IBM's list formatting or plain numbered lists

### IBM Accent Bar Pattern (Section Dividers)
Section divider slides use a thick left-edge IBM Blue bar. When editing `slideLayout8.xml`-based slides, do not remove or recolor the `0F62FE` shape at the left edge.

---

## Workflow Summary

```
1. Copy IBM template (from the skill root):
   cp references/assets/ibm-template.pptx output.pptx

2. Unpack:
   python3 references/scripts/office/unpack.py output.pptx unpacked/

3. Map content → layouts (use names from table above)

4. Delete unused slides from ppt/presentation.xml <p:sldIdLst>

5. Add needed slides:
   python3 references/scripts/add_slide.py unpacked/ slideLayoutN.xml

6. Edit content in each slide XML
   - Replace placeholder text
   - Keep IBM Plex Sans Light font references intact
   - Keep IBM Blue (#0F62FE) accent shapes intact
   - Update footer text on every slide

7. Clean + Pack:
   python3 references/scripts/clean.py unpacked/
   python3 references/scripts/office/pack.py unpacked/ output.pptx --original references/assets/ibm-template.pptx

8. QA: check for placeholder text, then visual QA
   python3 -m markitdown output.pptx | grep -iE "firstname|lastname|client name|footer|click to edit"
```
