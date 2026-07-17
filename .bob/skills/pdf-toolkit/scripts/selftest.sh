#!/usr/bin/env bash
# selftest.sh — verify a pdf-toolkit install in one command.
#
# Generates a tiny multi-page sample PDF, then exercises the core operations:
#   info · merge · split · rotate · pages · encrypt/decrypt · extract
# Prints a PASS/FAIL summary and exits non-zero if anything failed.
#
# Usage:  bash scripts/selftest.sh
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PY=${PYTHON:-python3}

pass=0; fail=0
ok()   { echo "  PASS  $1"; pass=$((pass+1)); }
bad()  { echo "  FAIL  $1"; fail=$((fail+1)); }
check(){ if [ "$1" -eq 0 ]; then ok "$2"; else bad "$2"; fi; }

echo "pdf-toolkit selftest"
echo "workdir: $WORK"
echo

# 0. Generate a 3-page sample PDF (reportlab). Skips gracefully if unavailable.
if ! "$PY" - "$WORK/sample.pdf" <<'PY'
import sys
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
except ImportError:
    sys.exit(3)
c = canvas.Canvas(sys.argv[1], pagesize=A4)
for i in range(1, 4):
    c.setFont("Helvetica", 24)
    c.drawString(72, 720, f"Sample page {i}")
    c.setFont("Helvetica", 12)
    c.drawString(72, 680, f"pdf-toolkit selftest — the secret token is ALPHA{i}.")
    c.showPage()
c.save()
PY
then
    echo "SKIP: reportlab not installed — cannot generate sample PDF."
    echo "      install with: pip install reportlab   (then re-run)"
    exit 3
fi
[ -s "$WORK/sample.pdf" ] && ok "generate sample.pdf (reportlab)" || bad "generate sample.pdf"

# 1. info reports 3 pages
"$PY" "$HERE/pdf_ops.py" info "$WORK/sample.pdf" | grep -q '"pages": 3'
check $? "info reports 3 pages"

# 2. merge (sample + sample -> 6 pages)
"$PY" "$HERE/pdf_ops.py" merge "$WORK/sample.pdf" "$WORK/sample.pdf" -o "$WORK/merged.pdf" >/dev/null
"$PY" "$HERE/pdf_ops.py" info "$WORK/merged.pdf" | grep -q '"pages": 6'
check $? "merge -> 6 pages"

# 3. split into per-page files (expect 3)
"$PY" "$HERE/pdf_ops.py" split "$WORK/sample.pdf" --outdir "$WORK/split" >/dev/null
[ "$(ls "$WORK"/split/*.pdf 2>/dev/null | wc -l | tr -d ' ')" = "3" ]
check $? "split -> 3 files"

# 4. pages: extract 1,3 -> 2 pages
"$PY" "$HERE/pdf_ops.py" pages "$WORK/sample.pdf" "1,3" -o "$WORK/subset.pdf" >/dev/null
"$PY" "$HERE/pdf_ops.py" info "$WORK/subset.pdf" | grep -q '"pages": 2'
check $? "pages 1,3 -> 2 pages"

# 5. rotate all pages 90
"$PY" "$HERE/pdf_ops.py" rotate "$WORK/sample.pdf" -o "$WORK/rot.pdf" --degrees 90 >/dev/null
check $? "rotate 90"

# 6a. encrypt: info (no password) should report encrypted:true
"$PY" "$HERE/pdf_ops.py" encrypt "$WORK/sample.pdf" -o "$WORK/enc.pdf" --user-password t0p >/dev/null
"$PY" "$HERE/pdf_ops.py" info "$WORK/enc.pdf" | grep -q '"encrypted": true'
check $? "encrypt (AES-256) — info shows encrypted"
# 6b. content ops without the password must be refused (exit 1)
"$PY" "$HERE/pdf_ops.py" pages "$WORK/enc.pdf" "1" -o "$WORK/nope.pdf" >/dev/null 2>&1
[ "$?" -eq 1 ]
check $? "encrypted content refused without password"
# 6c. decrypt with password -> readable 3-page PDF
"$PY" "$HERE/pdf_ops.py" --password t0p decrypt "$WORK/enc.pdf" -o "$WORK/dec.pdf" >/dev/null
"$PY" "$HERE/pdf_ops.py" info "$WORK/dec.pdf" | grep -q '"pages": 3'
check $? "decrypt with password -> readable"

# 7. extract text and confirm the known token is present
"$PY" "$HERE/extract.py" "$WORK/sample.pdf" --to text 2>/dev/null | grep -q "ALPHA2"
check $? "extract text (found known token)"

# 8. extract json is well-formed
"$PY" "$HERE/extract.py" "$WORK/sample.pdf" --to json 2>/dev/null \
  | "$PY" -c "import json,sys; json.load(sys.stdin)"
check $? "extract json (valid)"

echo
echo "----------------------------------------"
echo "RESULT: $pass passed, $fail failed"
[ "$fail" -eq 0 ] && { echo "ALL GREEN ✅"; exit 0; } || { echo "FAILURES ❌"; exit 1; }
