#!/bin/bash
# start-kb.sh — Start a Bob Shell knowledge-manager session for a project.
#
# Usage:
#   ./scripts/start-kb.sh                  # use current directory
#   ./scripts/start-kb.sh ~/Projects/myapp # cd to project first
#
# What it does:
#   1. Optionally cd to a project directory (first argument).
#   2. Verifies the KB is initialised (docs/knowledge-base/ exists).
#   3. Launches Bob Shell in knowledge-manager mode.
#
# Requirements:
#   - Bob Shell installed and knowledge-manager mode installed globally
#     (run scripts/install.sh once if not already done).
#   - docs/knowledge-base/ initialised in the target project
#     (run scripts/init-project.sh once if not already done).
set -e

# ── 1. Navigate to project directory (optional first argument) ──────────────
if [ -n "$1" ]; then
    cd "$1" || { echo "❌ Cannot cd to: $1"; exit 1; }
fi

PROJECT_DIR="$(pwd)"
KB_DIR="$PROJECT_DIR/docs/knowledge-base"

echo "📚 Starting Knowledge Manager session"
echo "   Project : $PROJECT_DIR"

# ── 2. Verify KB is initialised ─────────────────────────────────────────────
if [ ! -d "$KB_DIR" ]; then
    echo ""
    echo "❌ Knowledge base not found at: $KB_DIR"
    echo ""
    echo "Initialise the KB first:"
    echo "  ~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh"
    exit 1
fi

# Quick stats so the user knows what they're resuming
DOC_COUNT=$(find "$KB_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "   KB docs : $DOC_COUNT document(s) in $KB_DIR"

# Remind user of the resume prompt if CONTEXT.md exists
if [ -f "$PROJECT_DIR/CONTEXT.md" ]; then
    echo "   Context : CONTEXT.md present (auto-loaded by Bob)"
fi

echo ""

# ── 3. Launch Bob Shell in knowledge-manager mode ───────────────────────────
exec bob --chat-mode=knowledge-manager
