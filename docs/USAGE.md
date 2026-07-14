# Usage Guide

This guide covers how to use Bob Shell Knowledge Manager in your daily workflow.

## Quick Start

### 1. Initialize Knowledge Base

```bash
cd ~/Projects/your-project
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh
```

### 2. Start Bob Shell

```bash
bob --chat-mode=knowledge-manager
```

### 3. Create Your First Document

```
Research Cassandra's gossip protocol and create a concept document
```

Bob Shell will:
- Research the topic using web_fetch
- Create `docs/knowledge-base/concepts/gossip-protocol.md`
- Follow the concept template
- Save key facts to memory
- Update INDEX.md

## Basic Usage

### Creating Documents

#### Concept Documents

```
Research [topic] and create a concept document
```

Example:
```
Research CAP theorem and create a concept document
```

Result: `docs/knowledge-base/concepts/cap-theorem.md`

#### Guide Documents

```
Create a guide for [task]
```

Example:
```
Create a guide for setting up a Cassandra cluster
```

Result: `docs/knowledge-base/guides/cassandra-cluster-setup-guide.md`

#### Reference Documents

```
Create a reference document for [API/component]
```

Example:
```
Create a reference document for the REST API
```

Result: `docs/knowledge-base/references/rest-api-reference.md`

#### Research Documents

```
Research [topic] and document findings
```

Example:
```
Research performance optimization techniques and document findings
```

Result: `docs/knowledge-base/research/performance-optimization-2026-07.md`

### Searching Knowledge Base

```
What do we know about [topic]?
```

Bob Shell will:
1. Recall saved facts from memory
2. Search knowledge base files
3. Read relevant documents
4. Synthesize comprehensive answer
5. Provide document references

Example:
```
What do we know about Cassandra consistency levels?
```

### Updating Documents

```
Update [document] with [new information]
```

Example:
```
Update the gossip-protocol concept with information about failure detection
```

### Organizing Knowledge Base

```
Review and organize all [category] documents
```

Example:
```
Review and organize all concept documents
```

Bob Shell will:
- List all documents in category
- Check for missing cross-references
- Add "Related Documents" sections
- Update INDEX.md

## Common Workflows

### Workflow 1: Daily Research Notes

**Morning Research Session**:

```bash
bob --chat-mode=knowledge-manager
```

```
Research today's topics:
1. Cassandra's new features in 4.1
2. Best practices for schema design
3. Performance tuning guidelines

Create appropriate documents for each topic.
```

**Save Key Facts**:

Bob Shell automatically uses `save_memory` to persist important facts.

**Review Later**:

```
What did we learn about Cassandra 4.1 today?
```

### Workflow 2: Building a Concept Library

**Step 1: Identify Core Concepts**

```
Create concept documents for:
- CAP theorem
- Eventual consistency
- Quorum reads
- Hinted handoff
```

**Step 2: Link Concepts**

```
Update all consistency-related concepts to cross-reference each other
```

**Step 3: Verify Organization**

```
Review the concepts directory and ensure all documents are properly organized
```

### Workflow 3: Creating Project Documentation

**Step 1: System Architecture**

```
Create a concept document for our system architecture
```

**Step 2: Setup Guide**

```
Create a guide for setting up the development environment
```

**Step 3: API Reference**

```
Create a reference document for our REST API endpoints
```

**Step 4: Link Everything**

```
Update INDEX.md to include all new documents with proper categorization
```

### Workflow 4: Research Project

**Define Research Objective**:

```
Research distributed consensus algorithms and document findings
```

**Gather Sources**:

```
Research Paxos, Raft, and compare their approaches
```

**Document Analysis**:

```
Create a research document analyzing the trade-offs between Paxos and Raft
```

**Save Conclusions**:

Bob Shell automatically saves key findings to memory.

## Advanced Usage

### Custom Templates

You can reference the templates when creating documents:

```
Create a concept document for [topic] following the standard template
```

Templates are located in:
- `~/Projects/bob-llmwiki-knowledge-manager/config/templates/`

### Batch Operations

Create multiple documents at once:

```
Create concept documents for the following topics:
1. Distributed transactions
2. Two-phase commit
3. Saga pattern

Ensure they're all cross-referenced.
```

### Knowledge Base Maintenance

**Weekly Review**:

```
Review all documents created this week and:
1. Check for broken links
2. Ensure proper cross-referencing
3. Update INDEX.md
4. Identify documentation gaps
```

**Monthly Audit**:

```
Audit the entire knowledge base:
1. Check for outdated information
2. Identify documents that need updates
3. Suggest new documents based on gaps
4. Verify all cross-references are valid
```

### Exporting Knowledge Base

Export to different formats:

```bash
# Export as flat markdown
~/Projects/bob-llmwiki-knowledge-manager/scripts/export-kb.sh

# Export for Obsidian
~/Projects/bob-llmwiki-knowledge-manager/scripts/export-kb.sh obsidian

# Export as HTML (requires pandoc)
~/Projects/bob-llmwiki-knowledge-manager/scripts/export-kb.sh html

# Export as PDF (requires pandoc)
~/Projects/bob-llmwiki-knowledge-manager/scripts/export-kb.sh pdf
```

### Validation

Validate knowledge base integrity:

```bash
~/Projects/bob-llmwiki-knowledge-manager/scripts/validate-kb.sh
```

Checks:
- Required directories exist
- INDEX.md is present
- No broken links
- Provides statistics

## Tips and Best Practices

### Naming Conventions

Follow these conventions for consistency:

- **Concepts**: `concept-name.md` (e.g., `cap-theorem.md`)
- **Guides**: `task-name-guide.md` (e.g., `setup-guide.md`)
- **References**: `api-name-reference.md` (e.g., `rest-api-reference.md`)
- **Research**: `topic-YYYY-MM.md` (e.g., `performance-2026-07.md`)

### Cross-Referencing

Always include "Related Documents" sections:

```markdown
## Related Documents
- [Related Concept](./related-concept.md)
- [Related Guide](../guides/related-guide.md)
```

### Memory Management

Bob Shell's `save_memory` tool automatically persists key facts:

- Include context in facts
- Be specific and concise
- State relationships between concepts

### Regular Maintenance

- **Daily**: Save new facts, update INDEX.md
- **Weekly**: Review recent documents, check links
- **Monthly**: Audit entire knowledge base, update outdated info

### Version Control

Commit knowledge base changes regularly:

```bash
git add docs/knowledge-base/
git commit -m "Add concept: CAP theorem"
git push
```

## Troubleshooting

### Mode Not Available

**Issue**: knowledge-manager mode not found

**Solution**: Reinstall the mode:

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager
./scripts/install.sh
```

### Documents Not Created

**Issue**: Bob Shell doesn't create documents

**Solution**: Verify you're in knowledge-manager mode:

```
/mode knowledge-manager
```

### Search Not Finding Documents

**Issue**: Search doesn't find existing documents

**Solution**: Ensure documents are in the correct location:

```bash
ls -la docs/knowledge-base/
```

### Export Fails

**Issue**: Export script fails

**Solution**: Check format and dependencies:

```bash
# For HTML/PDF export, install pandoc
brew install pandoc  # macOS
```

## Examples

### Example 1: Software Development Project

```
# Initialize
cd ~/Projects/my-app
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh

# Start Bob Shell
bob --chat-mode=knowledge-manager

# Create architecture documentation
Create a concept document for our microservices architecture

# Create setup guide
Create a guide for setting up the development environment

# Create API reference
Create a reference document for our REST API

# Link everything
Update INDEX.md to include all new documents
```

### Example 2: Research Project

```
# Start Bob Shell
bob --chat-mode=knowledge-manager

# Research and document
Research machine learning optimization techniques and create a research document

# Save key findings
# (Bob Shell automatically saves to memory)

# Create related concepts
Create concept documents for:
- Gradient descent
- Backpropagation
- Learning rate scheduling

# Link research to concepts
Update the research document to reference the concept documents
```

### Example 3: Personal Wiki

```
# Start Bob Shell
bob --chat-mode=knowledge-manager

# Document learning
Create a concept document for Docker containers

# Create how-to guides
Create a guide for deploying applications with Docker

# Build knowledge over time
What do we know about containerization?

# Export for offline reading
~/Projects/bob-llmwiki-knowledge-manager/scripts/export-kb.sh obsidian
```

## Next Steps

- **Customize**: See [Customization Guide](CUSTOMIZATION.md)
- **Workflows**: See [Workflows Guide](WORKFLOWS.md)
- **Compare**: See [Comparison with LLM-Wiki](COMPARISON.md)

## Support

For issues or questions:

- [GitHub Issues](https://github.com/davidleconte/bob-llmwiki-knowledge-manager/issues)
- [Documentation](https://github.com/davidleconte/bob-llmwiki-knowledge-manager/tree/main/docs)
