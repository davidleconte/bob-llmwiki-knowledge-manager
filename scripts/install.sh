#!/bin/bash
set -e

echo "🚀 Installing Bob Shell Knowledge Manager..."

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTANT: Two distinct targets
#
#   Bob Shell CLI (this script):
#     • Config root: ~/.bob/   (or ~/.config/bob/)
#     • Mode file:   ~/.bob/custom_modes.yaml
#     • Activate:    bob --chat-mode=knowledge-manager
#     • Groups:      'command' = shell access, 'browser' = web access
#
#   Bob IDE (manual step — see below):
#     • Workspace file: .bob/custom_modes.yaml  (already in this repo)
#     • Global file:    ~/.bob/settings/custom_modes.yaml
#     • Groups differ:  'execute' not 'command', 'browser' not supported
#     • The Bob IDE-compatible entries are already appended to
#       .bob/custom_modes.yaml in this repository.  No install step needed;
#       they appear in the mode picker the moment you open the workspace.
#
# ─────────────────────────────────────────────────────────────────────────────

# Detect Bob Shell config directory
if [ -d "$HOME/.bob" ]; then
    BOB_CONFIG="$HOME/.bob"
elif [ -d "$HOME/.config/bob" ]; then
    BOB_CONFIG="$HOME/.config/bob"
else
    echo "❌ Bob Shell config directory not found"
    echo "Please ensure Bob Shell is installed"
    echo ""
    echo "If you are using Bob IDE (not Bob Shell CLI), no install is needed."
    echo "The knowledge-manager and repo-analyzer modes are already registered"
    echo "in .bob/custom_modes.yaml and appear in the mode picker automatically."
    exit 1
fi

echo "📁 Bob Shell config: $BOB_CONFIG"

# ─── Install mode for Bob Shell CLI ──────────────────────────────────────────
echo "📝 Installing knowledge-manager mode (Bob Shell CLI)..."

if [ -f "$BOB_CONFIG/custom_modes.yaml" ]; then
    echo "⚠️  custom_modes.yaml already exists — backing up to custom_modes.yaml.backup"
    cp "$BOB_CONFIG/custom_modes.yaml" "$BOB_CONFIG/custom_modes.yaml.backup"
fi

cp config/custom_modes.yaml "$BOB_CONFIG/custom_modes.yaml"

# ─── Install recommended settings (optional) ─────────────────────────────────
if [ ! -f "$BOB_CONFIG/settings.json" ]; then
    echo "📝 Installing recommended settings..."
    cp config/settings.json "$BOB_CONFIG/settings.json"
else
    echo "ℹ️  settings.json already exists (not overwriting)"
    echo "   See config/settings.json for recommended settings"
fi

echo ""
echo "✅ Bob Shell CLI installation complete!"
echo ""
echo "Next steps (Bob Shell CLI):"
echo "1. Initialize a knowledge base in your project:"
echo "   cd ~/Projects/your-project"
echo "   ~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh"
echo ""
echo "2. Start Bob Shell in knowledge-manager mode:"
echo "   bob --chat-mode=knowledge-manager"
echo ""
echo "──────────────────────────────────────────────────────────────────────────"
echo "Bob IDE users: no install needed."
echo "  - Open this workspace in Bob IDE."
echo "  - The 'Knowledge Manager' and 'Repository Analyzer' modes appear"
echo "    in the mode picker immediately (hot-reload from .bob/custom_modes.yaml)."
echo "  - To activate workflow instructions, run: use_skill(\"knowledge-manager\")"
echo "──────────────────────────────────────────────────────────────────────────"
