# PPTX Skill

A skill that teaches an AI assistant (e.g. **Bob**) to work with PowerPoint
files correctly — reading, editing, creating from scratch, and producing
IBM-branded presentations from the official IBM Carbon template.

## What it covers

- **Read** — extract text with `markitdown`, inspect thumbnails, view raw XML
- **Edit / template-based** — unpack → edit slide XML → clean → pack workflow
  with helper scripts for adding, deleting, and reordering slides
- **Create from scratch** — PptxGenJS for non-IBM presentations, with a full
  tutorial covering text, shapes, images, icons, tables, charts, and common
  pitfalls
- **IBM-branded presentations** — copy the bundled IBM Carbon template, map
  content to 48 named layouts, edit XML, and pack; IBM logo, fonts, cover
  imagery, and all branding assets are preserved automatically
- **Design principles** — color palettes, layout variety, typography, spacing,
  and what to avoid
- **QA** — content checks for leftover placeholders, visual QA via subagents,
  and a verification loop

## Layout

```
pptx-ibm-template/
├── SKILL.md              # the skill (loaded by the assistant)
├── README.md             # this file
└── references/           # loaded on demand by the skill
    ├── editing.md        # template-based workflow, slide operations, XML editing rules
    ├── pptxgenjs.md      # full PptxGenJS tutorial
    ├── ibm-template.md   # IBM Carbon design system, layouts, design rules, media guide
    ├── assets/
    │   └── ibm-template.pptx  # bundled IBM Carbon template (94 sample slides, 48 layouts)
    └── scripts/          # helper scripts (unpack, add_slide, clean, pack, thumbnail)
        └── office/
```

## IBM template

The bundled `references/assets/ibm-template.pptx` is the official IBM Carbon
presentation template. It contains:
- 94 sample slides covering all 48 named layouts
- IBM Plex Sans Light font wiring throughout the slide master
- IBM logo and branding imagery embedded in the master (inherited by all slides)
- Cover photos, pictograms, and decorative assets in `ppt/media/`

> **IBM presentations must always use the template workflow — never PptxGenJS.**
> See `references/ibm-template.md` for the full workflow and design rules.
