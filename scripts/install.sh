#!/bin/bash
set -e

echo "🚀 Installing Bob Shell Knowledge Manager..."

# Detect Bob Shell config directory
if [ -d "$HOME/.bob" ]; then
    BOB_CONFIG="$HOME/.bob"
elif [ -d "$HOME/.config/bob" ]; then
    BOB_CONFIG="$HOME/.config/bob"
else
    echo "❌ Bob Shell config directory not found"
    echo "Please ensure Bob Shell is installed"
    exit 1
fi

echo "📁 Bob Shell config: $BOB_CONFIG"

# Copy custom mode configuration
echo "📝 Installing knowledge-manager mode..."
if [ -f "$BOB_CONFIG/custom_modes.yaml" ]; then
    echo "⚠️  custom_modes.yaml already exists"
    echo "Backing up to custom_modes.yaml.backup"
    cp "$BOB_CONFIG/custom_modes.yaml" "$BOB_CONFIG/custom_modes.yaml.backup"
fi

cp config/custom_modes.yaml "$BOB_CONFIG/custom_modes.yaml"

# Copy recommended settings (optional)
if [ ! -f "$BOB_CONFIG/settings.json" ]; then
    echo "📝 Installing recommended settings..."
    cp config/settings.json "$BOB_CONFIG/settings.json"
else
    echo "ℹ️  settings.json already exists (not overwriting)"
    echo "   See config/settings.json for recommended settings"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Initialize a knowledge base in your project:"
echo "   cd ~/Projects/your-project"
echo "   ~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh"
echo ""
echo "2. Start Bob Shell in knowledge-manager mode:"
echo "   bob --chat-mode=knowledge-manager"
