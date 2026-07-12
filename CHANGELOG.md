# Changelog

All notable changes to Bob Shell Knowledge Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-12

### Added
- Initial release of Bob Shell Knowledge Manager
- Custom knowledge-manager mode for Bob Shell
- Four document templates (concept, guide, reference, research)
- Knowledge base structure (concepts, guides, references, research)
- Automation scripts:
  - `install.sh` - Install mode to Bob Shell
  - `init-project.sh` - Initialize KB structure in projects
  - `validate-kb.sh` - Validate KB structure and integrity
  - `export-kb.sh` - Export KB to multiple formats (markdown, Obsidian, HTML, PDF)
- Comprehensive documentation:
  - Quick Start Guide (5-minute setup)
  - Installation Guide
  - Usage Guide
  - Customization Guide
  - Workflows Guide
  - Architecture Documentation
  - Comparison with LLM-Wiki
- Three complete example knowledge bases:
  - Software project (e-commerce platform, 7 documents)
  - Research project (consensus algorithms, 6 documents)
  - Personal wiki (knowledge management, 6 documents)
- Comprehensive test suite:
  - 45 automated tests (100% passing)
  - Mode configuration validation (10 tests)
  - Template structure verification (16 tests)
  - Script functionality and syntax (19 tests)
  - pytest configuration with unit/integration markers

### Features
- Structured knowledge organization with four document types
- Full-text search across all documents using Bob Shell's native tools
- Persistent memory integration with save_memory tool
- Automatic cross-referencing between documents
- Template-driven document creation
- Zero external dependencies (uses only Bob Shell native features)
- Export to multiple formats (markdown, Obsidian, HTML, PDF)
- File restrictions to protect knowledge base integrity
- Naming conventions enforcement
- INDEX.md automatic maintenance

### Documentation
- README with badges, quick start, and comprehensive overview
- Quick Start Guide for 5-minute setup
- Detailed installation instructions
- Usage patterns and workflows
- Customization options
- Architecture documentation
- Feature comparison with LLM-Wiki
- Three working examples with best practices

### Testing
- pytest configuration with markers
- 10 mode configuration tests
- 16 template structure tests
- 19 workflow and integration tests
- Bash syntax validation for all scripts
- Example knowledge base integrity checks

## [Unreleased]

### Planned
- GitHub repository creation
- v1.0.0 release tag
- Community sharing and feedback
- Video tutorial/demo
- Additional export formats
- Integration with more Bob Shell features

---

For more information, see the [README](README.md) and [documentation](docs/).
