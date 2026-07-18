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

# ── Install mnemox shell function ─────────────────────────────────────────────
# Resolve the KM repo path (this script lives in <KM_HOME>/scripts/)
KM_INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MNEMOX_SHELL_FILE="$BOB_CONFIG/mnemox.sh"

cat > "$MNEMOX_SHELL_FILE" << MNEMOXEOF
# Mnemox Knowledge Builder — shell integration
# Installed by scripts/install.sh from: $KM_INSTALL_DIR
# Override MNEMOX_HOME at any time by exporting a different value.
export MNEMOX_HOME="${KM_INSTALL_DIR}"
mnemox() { bash "\$MNEMOX_HOME/scripts/mnemox.sh" "\$@"; }
MNEMOXEOF

echo ""
echo "✅ mnemox command installed → $MNEMOX_SHELL_FILE"
echo "   MNEMOX_HOME default: $KM_INSTALL_DIR"
echo ""

# Check if source line already exists in common shell rc files
SOURCE_LINE="source \"$MNEMOX_SHELL_FILE\""
RC_HINT_SHOWN=false
for RC_FILE in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile"; do
    if [[ -f "$RC_FILE" ]] && grep -qF "$MNEMOX_SHELL_FILE" "$RC_FILE" 2>/dev/null; then
        RC_HINT_SHOWN=true
        break
    fi
done

if [[ "$RC_HINT_SHOWN" == false ]]; then
    echo "──────────────────────────────────────────────────────────────────────────"
    echo "To activate the 'mnemox' command in your terminal, add this line to your"
    echo "shell config (~/.zshrc or ~/.bashrc):"
    echo ""
    echo "  $SOURCE_LINE"
    echo ""
    echo "Then reload your shell: source ~/.zshrc  (or open a new terminal)"
    echo "──────────────────────────────────────────────────────────────────────────"
fi

echo ""
echo "Next steps (Bob Shell CLI):"
echo "1. Activate mnemox in your terminal (see above), then:"
echo "   cd ~/your-project && mnemox"
echo ""
echo "2. Or use the three-script path directly:"
echo "   cd ~/Projects/your-project"
echo "   $KM_INSTALL_DIR/scripts/init-project.sh"
echo ""
echo "3. Start Bob Shell in 🧠 Mnemox Knowledge Builder mode:"
echo "   bob --chat-mode=knowledge-manager"
echo ""
echo "──────────────────────────────────────────────────────────────────────────"
echo "Bob IDE users: no install needed."
echo "  - Open this workspace in Bob IDE."
echo "  - The '🧠 Mnemox Knowledge Builder' mode appears in the mode picker"
echo "    immediately (hot-reload from .bob/custom_modes.yaml)."
echo "  - Type 'mnemox your workspace' in the chat to initialise or update."
echo "  - To load templates: use_skill(\"knowledge-manager\")"
echo "──────────────────────────────────────────────────────────────────────────"
