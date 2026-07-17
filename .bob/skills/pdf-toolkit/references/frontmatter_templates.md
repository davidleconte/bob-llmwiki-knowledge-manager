# Client Engineering — YAML Frontmatter Templates

Drop-in YAML front matter for `generate_pdf.py -e` (Eisvogel). Each block is a
ready-to-use **Client Engineering deliverable** style, using the IBM Carbon color
palette. Replace the placeholders and keep the fields you need.

> The `titlepage-color` value is what actually drives the theme — you can use any
> Carbon hex regardless of the `-t` label. All fields below are Eisvogel-recognized
> and render on the title page / running footer; extra keys are ignored safely.

Fields worth setting on every engagement deliverable:

| Field | Purpose |
|---|---|
| `subtitle` | engagement / client context, e.g. `"Prepared for Acme Corp · Discovery Sprint"` |
| `author` | list of `Name — Role` (Client Engineering squad) |
| `footer-left` | confidentiality + engagement code |
| `logo` / `logo-width` | *(optional)* client or IBM mark on the title page — commented out by default; uncomment and set a path to enable |
| `toc-own-page` | table of contents on its own page (longer deliverables) |

---

## 1. Discovery & Framing Brief — IBM Blue (`0f62fe`)

```yaml
---
title: "Discovery & Framing Brief"
subtitle: "Prepared for <Client> · Discovery Sprint"
author:
  - "<Name> — Client Engineering Lead"
  - "<Name> — Solution Architect"
date: "2026-07-02"
lang: en
titlepage: true
titlepage-color: "0f62fe"
titlepage-text-color: "ffffff"
titlepage-rule-color: "ffffff"
titlepage-rule-height: 2
# logo: "assets/logo.png"   # optional: uncomment and set a path to show a mark
# logo-width: 90
book: true
toc-own-page: true
footer-left: "IBM Client Engineering — Confidential"
---
```

## 2. Proof of Concept (PoC) Report — Blue 90 (`001d6c`)

```yaml
---
title: "Proof of Concept — Findings & Results"
subtitle: "Prepared for <Client> · <Use Case>"
author:
  - "<Name> — Data Scientist"
  - "<Name> — Engineer"
date: "2026-07-02"
lang: en
titlepage: true
titlepage-color: "001d6c"
titlepage-text-color: "ffffff"
titlepage-rule-color: "4589ff"
titlepage-rule-height: 2
# logo: "assets/logo.png"   # optional: uncomment and set a path to show a mark
# logo-width: 90
book: true
toc-own-page: true
footer-left: "IBM Client Engineering — PoC Report — Confidential"
---
```

## 3. Solution Blueprint / Architecture — Purple 60 (`8a3ffc`)

```yaml
---
title: "Solution Blueprint"
subtitle: "Target Architecture & Delivery Plan for <Client>"
author:
  - "<Name> — Solution Architect"
date: "2026-07-02"
lang: en
titlepage: true
titlepage-color: "8a3ffc"
titlepage-text-color: "ffffff"
titlepage-rule-color: "ffffff"
titlepage-rule-height: 2
# logo: "assets/logo.png"   # optional: uncomment and set a path to show a mark
# logo-width: 90
book: true
toc-own-page: true
footer-left: "IBM Client Engineering — Blueprint — Confidential"
---
```

## 4. Executive Summary / Business Case — Carbon Gray 100 (`161616`)

```yaml
---
title: "Executive Summary"
subtitle: "Business Case & Recommendation for <Client>"
author:
  - "IBM Client Engineering"
date: "2026-07-02"
lang: en
titlepage: true
titlepage-color: "161616"
titlepage-text-color: "ffffff"
titlepage-rule-color: "0f62fe"
titlepage-rule-height: 3
# logo: "assets/logo.png"   # optional: uncomment and set a path to show a mark
# logo-width: 90
book: false
footer-left: "IBM Client Engineering — Confidential"
---
```

## 5. Working Session / Sprint Readout — Teal 60 (`007d79`)

```yaml
---
title: "Sprint Readout"
subtitle: "Working Session Summary · <Client> · Sprint <N>"
author:
  - "IBM Client Engineering Squad"
date: "2026-07-02"
lang: en
titlepage: true
titlepage-color: "007d79"
titlepage-text-color: "ffffff"
titlepage-rule-color: "ffffff"
titlepage-rule-height: 2
# logo: "assets/logo.png"   # optional: uncomment and set a path to show a mark
# logo-width: 90
book: false
footer-left: "IBM Client Engineering — Internal / Client-Shared"
---
```

---

## IBM Carbon Palette Reference

| Deliverable | Token | Hex |
|---|---|---|
| Discovery & Framing | Blue 60 | `0f62fe` |
| Proof of Concept | Blue 90 | `001d6c` |
| Solution Blueprint | Purple 60 | `8a3ffc` |
| Executive Summary | Gray 100 | `161616` |
| Sprint Readout | Teal 60 | `007d79` |
| Accent (rules/links) | Blue 50 | `4589ff` |
| Success / positive | Green 50 | `24a148` |
| Warning / risk | Yellow 30 | `f1c21b` |

Text color on all dark title pages: white (`ffffff`).
