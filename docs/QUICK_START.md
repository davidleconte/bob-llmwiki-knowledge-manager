# Quick Start Guide

Get started with Bob Shell Knowledge Manager in 5 minutes.

## Prerequisites

- Bob Shell installed and configured
- Basic familiarity with markdown

## Installation (2 minutes)

```bash
# Clone or download the project
cd ~/Projects/bob-llmwiki-knowledge-manager

# Install the knowledge-manager mode
./scripts/install.sh

# Restart Bob Shell to load the new mode
```

## Initialize Your First Knowledge Base (1 minute)

```bash
# Navigate to your project
cd ~/your-project

# Initialize knowledge base structure
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh

# Verify the structure
ls -la docs/knowledge-base/
```

You should see:
```
docs/knowledge-base/
├── INDEX.md
├── concepts/
├── guides/
├── references/
└── research/
```

## Create Your First Document (2 minutes)

### Option 1: Using Bob Shell (Recommended)

1. Open Bob Shell in your project
2. Switch to knowledge-manager mode: `bob mode knowledge-manager`
3. Ask Bob to create a document:
   ```
   Create a concept document about "microservices architecture"
   ```

Bob will:
- Use the appropriate template
- Follow naming conventions
- Add cross-references
- Update INDEX.md
- Save key facts to memory

### Option 2: Manual Creation

```bash
# Copy a template
cp ~/Projects/bob-llmwiki-knowledge-manager/config/templates/concept.md \
   docs/knowledge-base/concepts/microservices-architecture.md

# Edit the document
# Update INDEX.md
```

## Verify Your Setup

```bash
# Validate knowledge base structure
~/Projects/bob-llmwiki-knowledge-manager/scripts/validate-kb.sh

# Should output: ✅ Knowledge base structure is valid
```

## Next Steps

- **Learn workflows**: Read [WORKFLOWS.md](WORKFLOWS.md)
- **Customize**: See [CUSTOMIZATION.md](CUSTOMIZATION.md)
- **Explore examples**: Check `examples/` directory
- **Export**: Use `scripts/export-kb.sh` for different formats

## Common Tasks

### Search for Information
```bash
# In Bob Shell (knowledge-manager mode)
"Search the knowledge base for information about authentication"
```

### Update INDEX.md
```bash
# Bob Shell will automatically update it, or manually:
# Edit docs/knowledge-base/INDEX.md
```

### Export Knowledge Base
```bash
# Export as markdown
./scripts/export-kb.sh markdown

# Export as HTML (requires pandoc)
./scripts/export-kb.sh html
```

## Troubleshooting

**Mode not showing up?**
- Restart Bob Shell
- Check `~/.bob/custom_modes.yaml` exists
- Verify installation: `cat ~/.bob/custom_modes.yaml | grep knowledge-manager`

**Templates not found?**
- Ensure project is at `~/Projects/bob-llmwiki-knowledge-manager`
- Check templates exist: `ls ~/Projects/bob-llmwiki-knowledge-manager/config/templates/`

**Need help?**
- Read [USAGE.md](USAGE.md) for detailed instructions
- Check [WORKFLOWS.md](WORKFLOWS.md) for common patterns
- Review examples in `examples/` directory

## What's Next?

You're ready to build your knowledge base! The knowledge-manager mode will:
- Guide you through document creation
- Maintain consistent structure
- Keep cross-references updated
- Save important facts to memory
- Help you find information quickly

Happy documenting! 📚
