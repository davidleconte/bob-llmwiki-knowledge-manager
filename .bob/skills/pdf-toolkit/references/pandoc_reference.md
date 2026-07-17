# Pandoc Commands Reference

## Basic PDF Generation
```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex
```

## With Table of Contents
```bash
pandoc input.md -o output.pdf --pdf-engine=xelatex --toc --toc-depth=2
```

## Russian Documents (EB Garamond)
```bash
pandoc input-ru.md -o output.pdf --pdf-engine=xelatex -V mainfont="EB Garamond"
```

## Desktop / A4 Full Command
```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=2 \
  -V geometry:margin=2.5cm \
  -V fontsize=11pt \
  -V documentclass=article \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue
```

## Mobile (6×9) Full Command
```bash
pandoc input.md -o output-mobile.pdf \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=2 \
  -V geometry:paperwidth=6in \
  -V geometry:paperheight=9in \
  -V geometry:margin=0.5in \
  -V fontsize=10pt \
  -V linestretch=1.2 \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue
```

## Install Dependencies (macOS)
```bash
brew install pandoc
brew install --cask mactex
```
