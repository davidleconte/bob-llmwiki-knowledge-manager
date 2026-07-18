#!/usr/bin/env bash
# =============================================================================
# add-frontmatter.sh — Automatically add YAML frontmatter to KB docs that lack it
#
# Called by mnemox.sh on every update pass (idempotent — skips docs that
# already have frontmatter).
#
# For each *.md file in the four KB category directories:
#   1. Skip if file already starts with ---
#   2. Derive title from the first # heading (or the filename stem)
#   3. Derive category from the directory name
#   4. Derive tags from the category (concepts get compact-summary)
#   5. Set created/updated to the file's mtime date (YYYY-MM-DD)
#   6. Prepend the frontmatter block
#
# Usage:
#   bash scripts/add-frontmatter.sh [KB_DIR]
#   KB_DIR defaults to docs/knowledge-base
#
# Outputs one line per file processed:
#   ✅ Added frontmatter: concepts/token-optimization.md
#   ⏭  Has frontmatter:  concepts/kb-tos-embedding-layer.md
# =============================================================================
set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

KB_DIR="${1:-docs/knowledge-base}"
CATEGORIES=(concepts guides references research)
ADDED=0
SKIPPED=0

for CAT in "${CATEGORIES[@]}"; do
    CAT_DIR="$KB_DIR/$CAT"
    [[ -d "$CAT_DIR" ]] || continue

    for FILE in "$CAT_DIR"/*.md; do
        [[ -f "$FILE" ]] || continue

        # Skip if frontmatter already present
        if [[ "$(head -1 "$FILE")" == "---" ]]; then
            SKIPPED=$((SKIPPED + 1))
            continue
        fi

        # ── Derive metadata ────────────────────────────────────────────────
        STEM=$(basename "$FILE" .md)

        # Title: first # heading, else humanise the filename stem
        TITLE=$(grep -m1 "^# " "$FILE" 2>/dev/null | sed 's/^# //' || true)
        if [[ -z "$TITLE" ]]; then
            # Convert kebab-case stem to Title Case
            TITLE=$(echo "$STEM" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')
        fi

        # Tags: category-based defaults; concepts get compact-summary
        case "$CAT" in
            concepts)   TAGS="[$CAT, compact-summary]" ;;
            guides)     TAGS="[$CAT]" ;;
            references) TAGS="[$CAT]" ;;
            research)   TAGS="[$CAT]" ;;
        esac

        # Dates: use file mtime (portable: macOS + Linux)
        if date --version >/dev/null 2>&1; then
            # GNU date
            MTIME=$(date -d "@$(stat -c %Y "$FILE")" +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)
        else
            # BSD date (macOS)
            MTIME=$(stat -f "%Sm" -t "%Y-%m-%d" "$FILE" 2>/dev/null || date +%Y-%m-%d)
        fi

        # ── Build frontmatter block ────────────────────────────────────────
        FRONTMATTER="---
title: \"${TITLE}\"
category: ${CAT}
tags: ${TAGS}
created: ${MTIME}
updated: ${MTIME}
status: active
---
"

        # ── Prepend atomically ─────────────────────────────────────────────
        TMP=$(mktemp)
        printf '%s\n' "$FRONTMATTER" | cat - "$FILE" > "$TMP"
        mv "$TMP" "$FILE"

        echo -e "${GREEN}✅ Added frontmatter: ${CAT}/$(basename "$FILE")${NC}"
        ADDED=$((ADDED + 1))
    done
done

echo -e "${CYAN}ℹ️  Frontmatter: ${ADDED} added, ${SKIPPED} already present${NC}"
