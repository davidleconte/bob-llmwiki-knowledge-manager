#!/usr/bin/env bash
# =============================================================================
# mnemox-lessons.sh — Capture lessons learned since last mnemox run
#
# Called by mnemox.sh on the update path. Never blocks (no set -e).
# Writes a dated research note to docs/knowledge-base/research/
# and appends its entry to index.md Recent Additions.
#
# Outputs MNEMOX_LESSONS_NOTE=<path> as the final stdout line so
# mnemox.sh and the Bob mode instruction can parse the note path.
# =============================================================================

# No set -e — this script must never block the update path
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

KB_DIR="docs/knowledge-base"
RESEARCH_DIR="$KB_DIR/research"
INDEX_FILE="$KB_DIR/index.md"
LAST_RUN_FILE=".mnemox-last-run"
TODAY=$(date +%Y-%m-%d)
NOTE_FILE="$RESEARCH_DIR/mnemox-update-${TODAY}.md"

# ── Resolve since-timestamp ───────────────────────────────────────────────────
if [[ -f "$LAST_RUN_FILE" ]]; then
    SINCE=$(cat "$LAST_RUN_FILE" | tr -d '[:space:]')
else
    SINCE="7 days ago"
fi

# ── Capture git log since last run ───────────────────────────────────────────
GIT_LOG=""
if git -C . rev-parse --git-dir &>/dev/null 2>&1; then
    GIT_LOG=$(git log --since="$SINCE" --oneline --no-merges 2>/dev/null || true)
fi

if [[ -z "$GIT_LOG" ]]; then
    GIT_LOG="(no commits since last mnemox run)"
fi

# ── Count KB docs per category ────────────────────────────────────────────────
count_docs() {
    local dir="$KB_DIR/$1"
    if [[ -d "$dir" ]]; then
        find "$dir" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' '
    else
        echo "0"
    fi
}

CONCEPTS_COUNT=$(count_docs "concepts")
GUIDES_COUNT=$(count_docs "guides")
REFERENCES_COUNT=$(count_docs "references")
RESEARCH_COUNT=$(count_docs "research")
TOTAL_COUNT=$(find "$KB_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')

# ── Ensure research dir exists ────────────────────────────────────────────────
mkdir -p "$RESEARCH_DIR"

# ── Write dated research note ────────────────────────────────────────────────
cat > "$NOTE_FILE" << NOTEEOF
# Mnemox Update — $TODAY

## Objective
Automated KB update run by \`mnemox\` on $TODAY.
This note captures what changed since the last run and provides a scaffold
for lessons learned — synthesised by Bob in the same session.

## Background
- Last mnemox run: $SINCE
- KB location: \`$KB_DIR\`

## Git Changes Since Last Run

\`\`\`
$GIT_LOG
\`\`\`

## KB State

| Category   | Documents |
|------------|-----------|
| Concepts   | $CONCEPTS_COUNT |
| Guides     | $GUIDES_COUNT |
| References | $REFERENCES_COUNT |
| Research   | $RESEARCH_COUNT |
| **Total**  | **$TOTAL_COUNT** |

## New Analysis Reports Filed

$(find "$RESEARCH_DIR" -name "*.md" -newer "$LAST_RUN_FILE" -type f 2>/dev/null | sort | while read -r f; do echo "- \`$f\`"; done || echo "(none newer than last run)")

## Findings

<!-- MNEMOX_SYNTHESISE: Bob — review the git changes and new analysis reports
above and write 3–5 concrete, specific lessons learned directly into this
section now. Replace this comment with the synthesised content.
Focus on: what changed in the codebase, what patterns emerged, what should
be remembered for the next session. Then update index.md with this note's entry. -->

## Conclusions

### Recommendations
<!-- Bob: add 1–3 actionable next steps based on the findings above -->

### Next Steps
<!-- Bob: add specific tasks for the next session -->

## Related Documents
- [Knowledge Base Index](../index.md)

---
*Generated: $TODAY — Mnemox Knowledge Builder*
*Category: Research*
NOTEEOF

echo -e "${GREEN}✅ Lessons note created: $NOTE_FILE${NC}"

# ── Update index.md Recent Additions ─────────────────────────────────────────
if [[ -f "$INDEX_FILE" ]]; then
    NOTE_RELATIVE="./research/mnemox-update-${TODAY}.md"
    INDEX_ENTRY="- $TODAY: [Mnemox Update — $TODAY]($NOTE_RELATIVE) - Research — automated KB update: git log, doc counts, lessons learned scaffold"

    # Insert after the "## Recent Additions" line using Python for safe UTF-8 handling
    python3 - "$INDEX_FILE" "$INDEX_ENTRY" << 'PYEOF'
import sys
path, entry = sys.argv[1], sys.argv[2]
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
out = []
inserted = False
for line in lines:
    out.append(line)
    if not inserted and line.strip() == '## Recent Additions':
        out.append(entry + '\n')
        inserted = True
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(out)
PYEOF

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ index.md updated${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not update index.md — add entry manually${NC}"
    fi
fi

# ── Emit parseable path for mnemox.sh ────────────────────────────────────────
# This MUST be the last stdout line — mnemox.sh greps for it
echo "MNEMOX_LESSONS_NOTE=$NOTE_FILE"
