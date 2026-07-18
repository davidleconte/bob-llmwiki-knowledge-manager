#!/usr/bin/env bash
# =============================================================================
# sync-skill-templates.sh — Keep .bob/skills/knowledge-manager/SKILL.md
#                           template blocks in sync with config/templates/
#
# Reads each template file from config/templates/ and replaces the matching
# fenced code block in SKILL.md.  Safe to run repeatedly (idempotent).
#
# Usage:
#   bash scripts/sync-skill-templates.sh [--km-home PATH]
#
# Called automatically by mnemox.sh (update path) when --full or --quick is run.
#
# Exit codes:
#   0  All blocks updated (or already current)
#   1  SKILL.md or a template file not found
# =============================================================================
set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Resolve paths ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KM_HOME="${1:-$(dirname "$SCRIPT_DIR")}"

# Allow --km-home flag
if [[ "${1:-}" == "--km-home" ]]; then
    KM_HOME="$2"
fi

TEMPLATES_DIR="$KM_HOME/config/templates"
SKILL_FILE="$KM_HOME/.bob/skills/knowledge-manager/SKILL.md"

# Validate
if [[ ! -f "$SKILL_FILE" ]]; then
    echo -e "${YELLOW}⚠️  SKILL.md not found: $SKILL_FILE — skipping sync${NC}"
    exit 1
fi
if [[ ! -d "$TEMPLATES_DIR" ]]; then
    echo -e "${YELLOW}⚠️  Templates dir not found: $TEMPLATES_DIR — skipping sync${NC}"
    exit 1
fi

# ── Map template filename → SKILL.md section heading ─────────────────────────
declare -A TEMPLATE_HEADING
TEMPLATE_HEADING[concept]="Concept"
TEMPLATE_HEADING[guide]="Guide"
TEMPLATE_HEADING[reference]="Reference"
TEMPLATE_HEADING[research]="Research"

UPDATED=0
SKIPPED=0

# ── Replace each fenced block ─────────────────────────────────────────────────
# Strategy: for each template, locate the ````markdown ... ```` fenced block
# that follows the matching ### heading, then replace its content with the
# current template file content.  Uses Python for reliable multi-line replace.
for NAME in concept guide reference research; do
    TMPL_FILE="$TEMPLATES_DIR/${NAME}.md"
    [[ -f "$TMPL_FILE" ]] || { echo -e "${YELLOW}⚠️  Missing template: $TMPL_FILE${NC}"; continue; }

    HEADING="${TEMPLATE_HEADING[$NAME]}"
    TMPL_CONTENT=$(cat "$TMPL_FILE")

    # Use Python to do the multi-line block replacement
    python3 - "$SKILL_FILE" "$HEADING" "$TMPL_CONTENT" <<'PYEOF'
import sys, re

skill_path = sys.argv[1]
heading    = sys.argv[2]
new_block  = sys.argv[3]

text = open(skill_path).read()

# Pattern: match the ````markdown ... ```` block under ### <Heading> (...)
# We look for the heading line, skip to the next ````markdown fence, then
# capture everything up to the closing ```` on its own line.
pattern = (
    r'(###\s+' + re.escape(heading) + r'[^\n]*\n\n)'   # heading + blank
    r'(````markdown\n)'                                  # opening fence
    r'(.*?)'                                             # current block content
    r'(````)'                                            # closing fence
)
replacement = r'\g<1>\g<2>' + re.escape(new_block).replace(r'\n', '\n') + r'\n\g<4>'

new_text, n = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)

# re.escape is overkill on replacement side — use a plain substitution instead
if n == 0:
    sys.exit(2)   # heading not found

# Redo without re.escape on the replacement content
def replacer(m):
    return m.group(1) + m.group(2) + new_block + '\n' + m.group(4)

new_text = re.sub(pattern, replacer, text, count=1, flags=re.DOTALL)

open(skill_path, 'w').write(new_text)
sys.exit(0)
PYEOF
    PY_EXIT=$?
    if [[ $PY_EXIT -eq 0 ]]; then
        echo -e "${GREEN}✅ Synced: ${NAME} template → SKILL.md${NC}"
        UPDATED=$((UPDATED + 1))
    elif [[ $PY_EXIT -eq 2 ]]; then
        echo -e "${YELLOW}⚠️  Heading '### ${HEADING}' not found in SKILL.md — skipping ${NAME}${NC}"
        SKIPPED=$((SKIPPED + 1))
    else
        echo -e "${YELLOW}⚠️  Python error for ${NAME} template — skipping${NC}"
        SKIPPED=$((SKIPPED + 1))
    fi
done

echo -e "${CYAN}ℹ️  Template sync: ${UPDATED} updated, ${SKIPPED} skipped${NC}"
