# Comparison Guide

How Bob Shell Knowledge Manager compares to other solutions.

## vs LLM-Wiki

### Similarities
- Structured knowledge organization
- Document templates
- Search capabilities
- Memory persistence

### Differences

**LLM-Wiki**:
- Plugin-based architecture
- Special command syntax (@wiki, $wiki-query)
- Multi-agent research
- Automated compilation

**Bob Shell Knowledge Manager**:
- Custom mode (no plugins needed)
- Natural language commands
- Single-agent workflow
- Manual organization with automation scripts

### When to Use Each

**Use LLM-Wiki if**:
- You use Claude Code
- You want automated multi-agent research
- You prefer command syntax
- You need automated compilation

**Use Bob Shell Knowledge Manager if**:
- You use Bob Shell
- You want natural language interaction
- You prefer manual control
- You want zero external dependencies

## vs Manual Documentation

### Advantages Over Manual

- Structured templates
- Automated cross-referencing
- Memory persistence
- Search capabilities
- Export to multiple formats

### When Manual is Better

- Very simple projects
- One-off documentation
- No need for structure
- Prefer complete control

## vs Obsidian

### Similarities
- Markdown-based
- Cross-referencing
- Search capabilities
- Export options

### Differences

**Obsidian**:
- Desktop application
- Graph view
- Plugins ecosystem
- Manual creation

**Bob Shell Knowledge Manager**:
- AI-assisted creation
- Automated organization
- Template-driven
- Command-line focused

### Integration

Bob Shell Knowledge Manager can export to Obsidian format for the best of both worlds.

## Bob Shell CLI vs Bob IDE

The Knowledge Manager mode runs on both surfaces. This table documents
machine-verified behavioural differences so you can choose the right
environment for your workflow.

| Dimension | Bob Shell CLI | Bob IDE |
|---|---|---|
| Installation | `scripts/install.sh` → `~/.bob/custom_modes.yaml` | Open workspace — zero steps |
| Mode activation | `bob --chat-mode=knowledge-manager` | Mode picker → 📚 Knowledge Manager |
| Config file | `~/.bob/custom_modes.yaml` | `.bob/custom_modes.yaml` (workspace) |
| Shell group name | `command` | `execute` |
| Web group name | `browser` | not supported |
| Skill lazy-load | not supported | `skill` group + `use_skill()` |
| `save_memory` tool | available | not available |
| Knowledge persistence | `save_memory` + markdown files | markdown files only |
| Hot-reload | restart required | immediate |
| Non-interactive flag | `-p "prompt"` | N/A |
| Bob version verified | 1.0.6 | 1.121.0+bob2.0.1 |

> **Note:** All facts in this table were machine-verified in the session of 2026-07-16.

## Summary

Bob Shell Knowledge Manager is ideal for:
- Bob Shell users
- AI-assisted documentation
- Structured knowledge bases
- Team collaboration
- Version-controlled documentation
