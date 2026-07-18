#!/usr/bin/env bash
# setup.sh — Full-stack integration setup for Bob Shell Knowledge Manager + Token Optimization System
#
# Sequences:
#   1. Install the Python Token Optimization System (pip/uv)
#   2. Build the KB embedding index and knowledge graph (bob-optimize graph-build)
#   3. Print integration status (bob-optimize kb-status)
#
# Idempotent: safe to run multiple times.
# Fallback-safe: exits 0 even when Python is absent; the Bash KB Manager works without TOS.
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh
#
# See: INTEGRATIONS.md, docs/kb-manager/ARCHITECTURE.md §2 (no-Python constraint)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KB_PATH="${KB_PATH:-docs/knowledge-base}"
MIN_PYTHON_MINOR=11

# ─── Colour helpers ───────────────────────────────────────────────────────────

ok()   { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }
info() { echo "ℹ️  $*"; }
hr()   { echo "────────────────────────────────────────────────"; }

# ─── Step 1: Detect Python ≥ 3.11 ────────────────────────────────────────────

detect_python() {
    local py_cmd=""

    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            local major minor
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "${major:-0}" -ge 3 ] && [ "${minor:-0}" -ge "$MIN_PYTHON_MINOR" ]; then
                py_cmd="$cmd"
                break
            fi
        fi
    done

    echo "$py_cmd"
}

# ─── Step 2: Install TOS ─────────────────────────────────────────────────────

install_tos() {
    local py_cmd="$1"
    info "Installing Token Optimization System (TOS)..."

    if command -v uv &>/dev/null; then
        info "Using uv for installation."
        uv pip install -e ".[dev,monitoring]" --quiet
    else
        "$py_cmd" -m pip install -e ".[dev,monitoring]" --quiet
    fi

    # Verify the CLI is available in PATH.
    if command -v bob-optimize &>/dev/null; then
        ok "bob-optimize installed: $(bob-optimize --version 2>/dev/null || echo 'ok')"
    else
        # May need to add site-packages bin to PATH; re-check via python -m src.
        if "$py_cmd" -m src --help &>/dev/null 2>&1; then
            ok "TOS installed (use 'python -m src' or add .venv/bin to PATH for bob-optimize)"
        else
            warn "Installation completed but bob-optimize not found in PATH."
            warn "Add your virtual-environment's bin/ directory to PATH and re-run."
            return 1
        fi
    fi
}

# ─── Step 3: Build KB index and knowledge graph ───────────────────────────────

build_index() {
    info "Building KB embedding index and knowledge graph..."
    info "  kb-path: $KB_PATH"

    if command -v bob-optimize &>/dev/null; then
        local BOB_OPT="bob-optimize"
    else
        local BOB_OPT="python -m src"
    fi

    # Try with MiniLM (semantic edges) first; fall back gracefully.
    if $BOB_OPT graph-build --kb-path "$KB_PATH" --with-semantic 2>/dev/null; then
        ok "KB index built (MiniLM semantic backend)"
    elif $BOB_OPT graph-build --kb-path "$KB_PATH" 2>/dev/null; then
        ok "KB index built (hashing backend — install sentence-transformers for MiniLM)"
    else
        warn "KB index build failed. Run manually: bob-optimize graph-build --kb-path $KB_PATH"
        return 1
    fi
}

# ─── Step 4: Print integration status ────────────────────────────────────────

print_status() {
    info "Checking integration status..."

    if command -v bob-optimize &>/dev/null; then
        bob-optimize kb-status --kb-path "$KB_PATH"
    else
        python -m src kb-status --kb-path "$KB_PATH" 2>/dev/null \
            || warn "Could not run kb-status — check bob-optimize is in PATH."
    fi
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
    hr
    echo "Bob Shell Knowledge Manager — Full Stack Setup"
    hr

    cd "$REPO_ROOT"

    local py_cmd
    py_cmd=$(detect_python)

    if [ -z "$py_cmd" ]; then
        warn "Python ≥ 3.${MIN_PYTHON_MINOR} not found."
        info "The Bash KB Manager works without Python. To enable the Token Optimization"
        info "System (p@3 retrieval improvement, token compression), install Python 3.11+"
        info "and re-run this script."
        hr
        ok "Bob Shell KB Manager ready (Bash-only mode)."
        ok "  Activate: bob --chat-mode=knowledge-manager"
        ok "  Or open this workspace in Bob IDE (mode picker → Knowledge Manager)."
        exit 0
    fi

    info "Python detected: $("$py_cmd" --version)"

    # Run steps sequentially; any failure is non-fatal (each step degrades gracefully).
    install_tos "$py_cmd" || warn "TOS install had issues — continuing."
    build_index            || warn "Index build had issues — you can run it manually later."
    print_status           || true

    hr
    ok "Setup complete."
    ok "  KB Manager: bob --chat-mode=knowledge-manager  (Bob Shell CLI)"
    ok "  KB Manager: mode picker → Knowledge Manager     (Bob IDE)"
    ok "  TOS CLI:    bob-optimize --help"
    ok "  Status:     bob-optimize kb-status"
    hr
}

main "$@"
