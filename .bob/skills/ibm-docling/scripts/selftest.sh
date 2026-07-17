#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# selftest.sh — verify the ibm-docling skill install end to end.
# Checks the toolchain, then runs a real conversion + evaluation on a tiny PDF.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail=0

say()  { printf '%s\n' "$*"; }
ok()   { printf '  ok   %s\n' "$*"; }
bad()  { printf '  FAIL %s\n' "$*"; fail=1; }

say "== toolchain =="
if command -v docling >/dev/null 2>&1; then ok "docling CLI on PATH"; else bad "docling CLI missing (pip install docling)"; fi
python3 -c "import docling" 2>/dev/null && ok "import docling" || bad "import docling (pip install docling)"
python3 -c "import docling_core" 2>/dev/null && ok "import docling_core" || bad "import docling_core (pip install docling-core)"
python3 - <<'PY' 2>/dev/null && ok "versions readable" || bad "cannot read versions"
from importlib.metadata import version
print("docling", version("docling"), "| docling-core", version("docling-core"))
PY

say "== make a tiny test PDF =="
python3 - "$TMP/sample.pdf" <<'PY' 2>/dev/null && ok "wrote sample.pdf" || bad "could not create sample PDF (pip install reportlab)"
import sys
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    c = canvas.Canvas(sys.argv[1], pagesize=letter)
    c.setFont("Helvetica", 14)
    c.drawString(72, 720, "Docling Self-Test Document")
    c.setFont("Helvetica", 11)
    c.drawString(72, 690, "This is a born-digital PDF used to verify conversion.")
    c.drawString(72, 670, "Section 1: Overview")
    c.showPage(); c.save()
except Exception as e:
    print(e); sys.exit(1)
PY

if [ -f "$TMP/sample.pdf" ]; then
  say "== convert (script) =="
  python3 "$HERE/docling_convert.py" "$TMP/sample.pdf" --to md --no-ocr -o "$TMP/sample.md" >/dev/null 2>"$TMP/conv.log" \
    && [ -s "$TMP/sample.md" ] && ok "docling_convert.py -> markdown" || { bad "docling_convert.py"; sed 's/^/    /' "$TMP/conv.log"; }

  python3 "$HERE/docling_convert.py" "$TMP/sample.pdf" --to json --no-ocr -o "$TMP/sample.json" >/dev/null 2>>"$TMP/conv.log" \
    && [ -s "$TMP/sample.json" ] && ok "docling_convert.py -> json" || bad "docling_convert.py json"

  say "== analyze =="
  python3 "$HERE/docling_analyze.py" "$TMP/sample.json" --json-only >/dev/null 2>&1 && ok "docling_analyze.py" || bad "docling_analyze.py"

  say "== evaluate =="
  python3 "$HERE/docling_evaluate.py" "$TMP/sample.json" --markdown "$TMP/sample.md" >/dev/null 2>&1 \
    && ok "docling_evaluate.py (status pass)" || bad "docling_evaluate.py"

  say "== chunk =="
  python3 "$HERE/docling_chunk.py" "$TMP/sample.json" -o "$TMP/chunks.jsonl" >/dev/null 2>&1 \
    && [ -s "$TMP/chunks.jsonl" ] && ok "docling_chunk.py -> jsonl" || bad "docling_chunk.py (needs a HF tokenizer download on first run)"
fi

say ""
if [ "$fail" -eq 0 ]; then say "ALL CHECKS PASSED"; else say "SOME CHECKS FAILED (see above)"; fi
exit "$fail"
