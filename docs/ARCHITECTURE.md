# Architecture Guide

Design decisions and architecture of Bob Shell Knowledge Manager.

## Design Principles

### 1. Zero External Dependencies
Uses only Bob Shell's native features:
- save_memory for persistence
- search_file_content for search
- File management tools
- No external databases or services

### 2. Template-Driven
Consistent structure through templates:
- Concept documents
- Guide documents
- Reference documents
- Research documents

### 3. Natural Language Interface
No special syntax required:
- "Research X and create a concept"
- "What do we know about Y?"
- "Update document Z"

### 4. Version Control Friendly
Plain markdown files:
- Git-compatible
- Human-readable
- Easy to diff
- Collaborative

## Architecture Components

### 1. Custom Mode
- Defines behavior
- Provides instructions
- Sets conventions
- Enforces standards

### 2. Document Templates
- Ensure consistency
- Guide structure
- Reduce decisions
- Improve quality

### 3. Automation Scripts
- install.sh: System setup
- init-project.sh: Project setup
- validate-kb.sh: Quality checks
- export-kb.sh: Format conversion

### 4. Directory Structure
docs/knowledge-base/
- INDEX.md
- concepts/
- guides/
- references/
- research/

## Design Decisions

### Why Custom Mode?
- Reusable across projects
- Consistent behavior
- Easy to share
- Simple to customize

### Why Markdown?
- Universal format
- Version control friendly
- Human-readable
- Tool-agnostic

### Why Templates?
- Consistency
- Quality
- Efficiency
- Onboarding

### Why Scripts?
- Automation
- Validation
- Export
- Integration

## Extensibility

### Adding Categories
Create new directories and update mode configuration.

### Custom Templates
Add templates to config/templates/ directory.

### Integration
Export to other formats (Obsidian, HTML, PDF).

### Team Sharing
Commit .bob/custom_modes.yaml to repository.

## Future Enhancements

Potential improvements:
- Advanced search with filters
- Knowledge graph visualization
- Automated link checking
- Integration with note-taking apps
- Multi-language support

## Technical Stack

- Language: Bash (scripts), YAML (config), Markdown (docs)
- Dependencies: Bob Shell, Git (optional), Pandoc (optional)
- Platform: macOS, Linux, Windows (WSL)

## Comparison with Alternatives

See Comparison Guide for detailed comparison with:
- LLM-Wiki
- Manual documentation
- Obsidian
- Other knowledge management tools
