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

# Create index.md
echo "📝 Creating index.md..."
TODAY=$(date +%Y-%m-%d)
cat > docs/knowledge-base/index.md <<INDEXEOF
# Knowledge Base Index

Last Updated: $TODAY

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

*Managed by [Bob Shell Knowledge Manager](https://github.com/davidleconte/bob-llmwiki-knowledge-manager)*
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
    "fileName": ["CONTEXT.md", "docs/knowledge-base/index.md"]
  }
}
SETTINGSEOF
else
    echo "ℹ️  .bob/settings.json already exists (not overwriting)"
fi

# Create CONTEXT.md (auto-loaded by Bob at every session start via .bob/settings.json)
PROJECT_NAME=$(basename "$(pwd)")
if [ ! -f "CONTEXT.md" ]; then
    echo "📝 Creating CONTEXT.md..."
    cat > CONTEXT.md <<CTXEOF
# $PROJECT_NAME — Knowledge Base Context

> Auto-loaded by Bob Shell at session start (declared in \`.bob/settings.json\`).
> Edit this file to give Bob immediate orientation for every new session.

## Project
- **Name:** $PROJECT_NAME
- **KB location:** \`docs/knowledge-base/\`
- **Initialised:** $TODAY

## Quick-start prompts for new sessions

**Resume previous work:**
\`\`\`
What did we document most recently? Summarise the KB and suggest what to work on next.
\`\`\`

**Research and document a new topic:**
\`\`\`
Research [topic] and create a concept document.
\`\`\`

**Find existing knowledge:**
\`\`\`
What do we know about [topic]?
\`\`\`

**Maintenance:**
\`\`\`
Review all documents created this week and ensure proper cross-referencing and index.md is current.
\`\`\`

## KB summary
<!-- Update this section as the KB grows -->
- Concepts: 0 documents
- Guides: 0 documents
- References: 0 documents
- Research: 0 documents

---
*Last updated: $TODAY — managed by Bob Shell knowledge-manager mode*
CTXEOF
else
    echo "ℹ️  CONTEXT.md already exists (not overwriting)"
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
echo "  ."
echo "  ├── CONTEXT.md            ← auto-loaded context for every session"
echo "  ├── .bob/settings.json    ← tells Bob to load CONTEXT.md + index.md"
echo "  └── docs/knowledge-base/"
echo "      ├── index.md"
echo "      ├── concepts/"
echo "      ├── guides/"
echo "      ├── references/"
echo "      └── research/"
echo ""
echo "Next steps:"
echo "1. Start a knowledge-manager session (quickest):"
echo "   ~/Projects/bob-llmwiki-knowledge-manager/scripts/start-kb.sh"
echo ""
echo "2. Or start Bob Shell directly:"
echo "   bob --chat-mode=knowledge-manager"
echo ""
echo "3. First prompt to try:"
echo "   \"Research [topic] and create a concept document\""
