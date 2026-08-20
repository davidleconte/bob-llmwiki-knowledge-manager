#!/usr/bin/env bash
# =============================================================================
# mnemox.sh — Mnemox Knowledge Builder: smart two-mode workspace command
#
# Usage:
#   bash scripts/mnemox.sh              # auto-detect mode (init or update)
#   bash scripts/mnemox.sh --init       # force init mode
#   bash scripts/mnemox.sh --update     # force update mode
#   bash scripts/mnemox.sh --km-home /path/to/mnemox-repo
#   MNEMOX_HOME=/path/to/mnemox-repo bash scripts/mnemox.sh
#
# Environment:
#   MNEMOX_HOME  Path to the Mnemox repo (default: auto-detected from this
#                script's own location). Can be overridden at any time by
#                exporting a different value before launching Bob or terminal.
#
# Exit codes:
#   0  Success (including graph-build warnings and git-commit skips)
#   1  Fatal error in init path only
# =============================================================================

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m'

# ── Resolve MNEMOX_HOME ───────────────────────────────────────────────────────
# Priority: MNEMOX_HOME env var → --km-home flag → script's own parent directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_KM_HOME="$(dirname "$SCRIPT_DIR")"

# Parse flags first (before we need KM_HOME)
MODE="auto"   # auto | init | update
SKIP_ANALYSIS=false   # set true by --quick
KM_HOME_FLAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --init)    MODE="init";   shift ;;
        --update)  MODE="update"; shift ;;
        --quick)   MODE="update"; SKIP_ANALYSIS=true;  shift ;;
        --full)    MODE="update"; SKIP_ANALYSIS=false; shift ;;
        --km-home) KM_HOME_FLAG="$2"; shift 2 ;;
        --help|-h)
            echo ""
            echo "Usage: mnemox [--init|--update|--quick|--full] [--km-home PATH]"
            echo ""
            echo "  --init      First-time setup: scaffold KB, run 7-phase analysis, validate"
            echo "  --update    Smart update — same as --full (default when KB exists)"
            echo "  --quick     Steps 2-6: frontmatter + template sync + lessons + validate + graph"
            echo "  --full      Steps 1-6: repo analysis + frontmatter + template sync + lessons + validate + graph"
            echo "  --km-home   Path to the Mnemox repo (overrides MNEMOX_HOME env var)"
            echo ""
            echo "Environment variables:"
            echo "  MNEMOX_HOME  Default: auto-detected from script location"
            echo "               Set this to use mnemox from any project directory."
            echo ""
            echo "  mnemox your workspace   — type this in any Bob session to trigger"
            echo "  mnemox --quick          — lessons + graph + commit, no analysis"
            echo "  mnemox --full           — full analysis + lessons + graph + commit"
            exit 0
            ;;
        *) echo "Unknown flag: $1 (try --help)"; exit 1 ;;
    esac
done

# Resolve in priority order
if [[ -n "${KM_HOME_FLAG:-}" ]]; then
    MNEMOX_HOME="$KM_HOME_FLAG"
elif [[ -n "${MNEMOX_HOME:-}" ]]; then
    : # already set in environment — use it
else
    MNEMOX_HOME="$DEFAULT_KM_HOME"
fi

# Validate MNEMOX_HOME
if [[ ! -f "$MNEMOX_HOME/scripts/init-project.sh" ]]; then
    echo -e "${RED}❌ MNEMOX_HOME does not point to a valid Mnemox repo: $MNEMOX_HOME${NC}"
    echo "   Set MNEMOX_HOME or use --km-home to specify the correct path."
    exit 1
fi

# ── Banner ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║   🧠  Mnemox Knowledge Builder                             ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Detect mode ───────────────────────────────────────────────────────────────
KB_INDEX="docs/knowledge-base/index.md"

if [[ "$MODE" == "auto" ]]; then
    if [[ -f "$KB_INDEX" ]]; then
        MODE="update"
    else
        MODE="init"
    fi
fi

if [[ "$MODE" == "update" && ! -f "$KB_INDEX" ]]; then
    echo -e "${RED}❌ --update requested but no KB found (missing $KB_INDEX).${NC}"
    echo "   Run without flags to auto-detect, or use --init to create a new KB."
    exit 1
fi

# =============================================================================
# INIT PATH
# =============================================================================
if [[ "$MODE" == "init" ]]; then
    echo -e "${MAGENTA}▶ Mode: INIT — Mnemoxing this workspace for the first time${NC}"
    echo ""

    # Step 1: scaffold
    echo -e "${CYAN}Step 1/3 · Scaffolding knowledge base...${NC}"
    bash "$MNEMOX_HOME/scripts/init-project.sh"

    # Step 2: full analysis
    echo ""
    echo -e "${CYAN}Step 2/3 · Running 7-phase repository analysis...${NC}"
    bash "$MNEMOX_HOME/scripts/run-full-analysis.sh"

    # Step 3: validate
    echo ""
    echo -e "${CYAN}Step 3/3 · Validating knowledge base structure...${NC}"
    bash "$MNEMOX_HOME/scripts/validate-kb.sh"

    # Write last-run timestamp
    date -u +"%Y-%m-%dT%H:%M:%SZ" > .mnemox-last-run

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✅  Workspace Mnemoxed!                                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  KB location : ${CYAN}docs/knowledge-base/${NC}"
    echo -e "  Documents   : $(find docs/knowledge-base -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ') files created"
    echo ""
    echo -e "${YELLOW}Next step: open the 🧠 Mnemox Knowledge Builder mode in Bob IDE${NC}"
    echo -e "${YELLOW}or run: bob --chat-mode=knowledge-manager${NC}"
    echo -e "${YELLOW}Then type: What did we document most recently? Summarise the KB.${NC}"
    echo ""
    echo -e "${YELLOW}Note: init does not auto-commit. Review the KB before committing:${NC}"
    echo -e "  git add docs/knowledge-base/ && git commit -m \"mnemox: initial KB\""
    exit 0
fi

# =============================================================================
# UPDATE PATH  (set -e is OFF for graceful degradation on graph/git)
# =============================================================================
set +e

if [[ "$SKIP_ANALYSIS" == true ]]; then
    echo -e "${MAGENTA}▶ Mode: UPDATE (quick) — lessons + graph + commit, no repo analysis${NC}"
else
    echo -e "${MAGENTA}▶ Mode: UPDATE (full) — analysis + lessons + graph + commit${NC}"
fi
echo ""

# Step 1: refresh analysis (skipped by --quick)
if [[ "$SKIP_ANALYSIS" == false ]]; then
    echo -e "${CYAN}Step 1/5 · Refreshing 7-phase repository analysis...${NC}"
    bash "$MNEMOX_HOME/scripts/run-full-analysis.sh"
    ANALYSIS_EXIT=$?
    if [[ $ANALYSIS_EXIT -ne 0 ]]; then
        echo -e "${YELLOW}⚠️  Analysis completed with warnings (exit $ANALYSIS_EXIT) — continuing${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}ℹ️  Step 1/6 · Skipping repo analysis (--quick mode)${NC}"
fi

# Step 2: add frontmatter to any KB docs that lack it (idempotent)
echo ""
echo -e "${CYAN}Step 2/6 · Ensuring frontmatter on all KB docs...${NC}"
bash "$MNEMOX_HOME/scripts/add-frontmatter.sh" docs/knowledge-base

# Step 3: sync SKILL.md template blocks from config/templates/ (idempotent)
echo ""
echo -e "${CYAN}Step 3/6 · Syncing SKILL.md template blocks...${NC}"
bash "$MNEMOX_HOME/scripts/sync-skill-templates.sh" --km-home "$MNEMOX_HOME"

# Step 4: capture lessons learned
echo ""
echo -e "${CYAN}Step 4/6 · Capturing lessons learned...${NC}"
LESSONS_OUTPUT=$(bash "$MNEMOX_HOME/scripts/mnemox-lessons.sh" 2>&1)
echo "$LESSONS_OUTPUT"
# Parse the MNEMOX_LESSONS_NOTE path from output
LESSONS_NOTE=$(echo "$LESSONS_OUTPUT" | grep '^MNEMOX_LESSONS_NOTE=' | tail -1 | cut -d'=' -f2-)

# Step 5: validate
echo ""
echo -e "${CYAN}Step 5/6 · Validating knowledge base structure...${NC}"
bash "$MNEMOX_HOME/scripts/validate-kb.sh"

# Step 6: rebuild knowledge graph (graceful — never blocks)
# bob-optimize lives in the mnemox repo (MNEMOX_HOME); run it from there so it
# works regardless of which project is being mnemoxed.
echo ""
echo -e "${CYAN}Step 6/6 · Rebuilding knowledge graph...${NC}"
if command -v uv &>/dev/null; then
    uv run --project "$MNEMOX_HOME" bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic
    GRAPH_EXIT=$?
    if [[ $GRAPH_EXIT -ne 0 ]]; then
        echo -e "${YELLOW}⚠️  Graph build returned exit $GRAPH_EXIT — continuing without graph update${NC}"
    else
        echo -e "${GREEN}✅ Knowledge graph rebuilt${NC}"
    fi
elif command -v bob-optimize &>/dev/null; then
    bob-optimize graph-build --kb-path docs/knowledge-base --with-semantic
    GRAPH_EXIT=$?
    if [[ $GRAPH_EXIT -ne 0 ]]; then
        echo -e "${YELLOW}⚠️  Graph build returned exit $GRAPH_EXIT — continuing without graph update${NC}"
    else
        echo -e "${GREEN}✅ Knowledge graph rebuilt${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  uv not found — skipping graph rebuild (install uv: https://docs.astral.sh/uv/)${NC}"
fi

# Stage KB changes on a review branch (ATK-MEM-04: no unreviewed direct-to-main commits)
echo ""
echo -e "${CYAN}Staging KB changes for review...${NC}"
if git -C . rev-parse --git-dir &>/dev/null; then
    git add docs/knowledge-base/
    COMMIT_DATE=$(date +%Y-%m-%d)
    if git diff --cached --quiet; then
        echo -e "${YELLOW}ℹ️  Nothing new to commit in docs/knowledge-base/${NC}"
    else
        BRANCH="kb/update-$(date +%Y-%m-%d-%H%M%S)"
        git checkout -b "$BRANCH" --quiet
        COMMIT_SHA=$(git commit -m "kb: staged update $COMMIT_DATE" --quiet && git rev-parse --short HEAD)
        echo -e "${GREEN}✅ Staged on branch ${BRANCH} (${COMMIT_SHA})${NC}"
        echo -e "${YELLOW}⚠  Review required before merging. Open a PR:${NC}"
        echo -e "     gh pr create --base main --head $BRANCH --title 'kb: update $COMMIT_DATE'"
        git checkout - --quiet 2>/dev/null || true
    fi
else
    echo -e "${YELLOW}⚠️  Not a git repository — skipping staging${NC}"
fi

# Write last-run timestamp
date -u +"%Y-%m-%dT%H:%M:%SZ" > .mnemox-last-run

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅  Mnemox update complete                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  KB location : ${CYAN}docs/knowledge-base/${NC}"
echo -e "  Documents   : $(find docs/knowledge-base -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ') total"

if [[ -n "${LESSONS_NOTE:-}" ]]; then
    echo -e "  Lessons note: ${CYAN}${LESSONS_NOTE}${NC}"
    echo ""
    echo -e "${MAGENTA}════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  MNEMOX_LESSONS_NOTE=${LESSONS_NOTE}${NC}"
    echo -e "${MAGENTA}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Bob: please read ${LESSONS_NOTE} and synthesise the lessons learned now.${NC}"
fi

echo ""
exit 0
