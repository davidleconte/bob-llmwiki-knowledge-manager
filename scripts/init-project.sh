#!/bin/bash
set -e

echo "📚 Initializing Knowledge Base..."

# Check if we're in a project directory
if [ ! -d ".git" ] && [ ! -f "package.json" ] && [ ! -f "pyproject.toml" ]; then
    echo "⚠️  Warning: This doesn't look like a project directory"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p docs/knowledge-base/{concepts,guides,references,research}

# Create INDEX.md
echo "📝 Creating INDEX.md..."
cat > docs/knowledge-base/INDEX.md << 'INDEXEOF'
# Knowledge Base Index

Last Updated: $(date +%Y-%m-%d)

## Quick Navigation
- [Concepts](./concepts/) - Core concepts and definitions
- [Guides](./guides/) - How-to guides and tutorials
- [References](./references/) - API documentation and specifications
- [Research](./research/) - Research notes and findings

## Recent Additions
<!-- Automatically updated by knowledge-manager mode -->

## All Documents

### Concepts
<!-- Automatically updated by knowledge-manager mode -->

### Guides
<!-- Automatically updated by knowledge-manager mode -->

### References
<!-- Automatically updated by knowledge-manager mode -->

### Research
<!-- Automatically updated by knowledge-manager mode -->

---

## Usage

This knowledge base is managed by Bob Shell in `knowledge-manager` mode.

### Getting Started
```bash
# Start Bob Shell in knowledge-manager mode
bob --chat-mode=knowledge-manager
```

### Common Tasks
- **Research a topic**: "Research [topic] and create a concept document"
- **Create a guide**: "Create a guide for [task]"
- **Find information**: "What do we know about [topic]?"
- **Update document**: "Update [document] with [new information]"
- **Organize**: "Review and organize all [category] documents"

---

*Managed by [Bob Shell Knowledge Manager](https://github.com/yourusername/bob-llmwiki-knowledge-manager)*
INDEXEOF

# Create .bob directory if it doesn't exist
if [ ! -d ".bob" ]; then
    echo "📁 Creating .bob directory..."
    mkdir -p .bob
fi

# Create or update .bob/settings.json
if [ ! -f ".bob/settings.json" ]; then
    echo "📝 Creating .bob/settings.json..."
    cat > .bob/settings.json << 'SETTINGSEOF'
{
  "context": {
    "fileName": ["CONTEXT.md", "docs/knowledge-base/INDEX.md"]
  }
}
SETTINGSEOF
else
    echo "ℹ️  .bob/settings.json already exists (not overwriting)"
fi

# Add to .gitignore if it exists
if [ -f ".gitignore" ]; then
    if ! grep -q "docs/knowledge-base/.DS_Store" .gitignore; then
        echo "📝 Updating .gitignore..."
        cat >> .gitignore << 'GITIGNOREEOF'

# Knowledge Base
docs/knowledge-base/.DS_Store
GITIGNOREEOF
    fi
fi

echo ""
echo "✅ Knowledge base initialized!"
echo ""
echo "Directory structure:"
echo "  docs/knowledge-base/"
echo "  ├── INDEX.md"
echo "  ├── concepts/"
echo "  ├── guides/"
echo "  ├── references/"
echo "  └── research/"
echo ""
echo "Next steps:"
echo "1. Start Bob Shell: bob --chat-mode=knowledge-manager"
echo "2. Try: 'Research [topic] and create a concept document'"
