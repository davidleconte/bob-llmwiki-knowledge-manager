# Bob Shell Knowledge Manager

A reusable knowledge management framework for Bob Shell, inspired by LLM-Wiki but built on Bob Shell's native capabilities.

[![Tests](https://img.shields.io/badge/tests-45%20passing-brightgreen)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- **Structured Knowledge Base** - Organized into concepts, guides, references, and research
- **Full-Text Search** - Search across all documents with context
- **Persistent Memory** - Save key facts with Bob Shell's save_memory tool
- **Automatic Cross-Referencing** - Maintain bidirectional links between documents
- **Document Templates** - Consistent structure for all document types
- **Custom Bob Shell Mode** - Optimized behavior for knowledge management
- **Zero External Dependencies** - Uses only Bob Shell's native features
- **Comprehensive Test Suite** - 45 tests ensuring quality and reliability

## Quick Start

**New to Bob Shell Knowledge Manager?** → [5-Minute Quick Start Guide](docs/QUICK_START.md)

### Installation

```bash
cd ~/Projects
git clone https://github.com/yourusername/bob-llmwiki-knowledge-manager.git
cd bob-llmwiki-knowledge-manager
./scripts/install.sh
```

### Initialize in Your Project

```bash
cd ~/Projects/your-project
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh
```

### Start Using

```bash
# Switch to knowledge-manager mode in Bob Shell
bob mode knowledge-manager

# Or start Bob Shell with the mode
bob --chat-mode=knowledge-manager
```

## Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started in 5 minutes ⚡
- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Usage Guide](docs/USAGE.md) - How to use the knowledge manager
- [Customization](docs/CUSTOMIZATION.md) - Customize templates and settings
- [Workflows](docs/WORKFLOWS.md) - Common workflows and patterns
- [Architecture](docs/ARCHITECTURE.md) - Technical architecture details
- [Comparison with LLM-Wiki](docs/COMPARISON.md) - Feature comparison

## Examples

Check out the `examples/` directory for three complete knowledge bases:
- **software-project** - E-commerce platform with microservices (7 documents)
- **research-project** - PhD thesis on consensus algorithms (6 documents)
- **personal-wiki** - Personal knowledge management (6 documents)

Each example demonstrates best practices for structure, cross-referencing, and documentation.

## Testing

The project includes a comprehensive test suite with 45 tests covering:
- Mode configuration validation (10 tests)
- Template structure verification (16 tests)
- Script functionality and syntax (19 tests)
- Example knowledge base integrity

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test suite
python3 -m pytest tests/test_mode_config.py -v
```

## Project Structure

```
bob-llmwiki-knowledge-manager/
├── config/
│   ├── custom_modes.yaml      # Knowledge manager mode definition
│   ├── settings.json          # Recommended Bob Shell settings
│   └── templates/             # Document templates (4 types)
├── scripts/
│   ├── install.sh            # Install mode to Bob Shell
│   ├── init-project.sh       # Initialize KB in project
│   ├── validate-kb.sh        # Validate KB structure
│   └── export-kb.sh          # Export to various formats
├── docs/                     # Comprehensive documentation
├── examples/                 # Three complete example KBs
├── tests/                    # 45 automated tests
└── README.md                 # This file
```

## Why Bob Shell Knowledge Manager?

### vs. LLM-Wiki
- **No MCP Server Required** - Uses Bob Shell's native tools
- **Faster Setup** - 5 minutes vs. 6-8 weeks of development
- **Simpler Architecture** - No complex server infrastructure
- **Full Integration** - Works seamlessly with Bob Shell modes

### vs. Manual Documentation
- **Structured Templates** - Consistent documentation format
- **Automatic Cross-References** - Maintain document relationships
- **Persistent Memory** - Bob remembers key facts across sessions
- **Search Integration** - Find information quickly with context

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [LLM-Wiki](https://github.com/nvk/llm-wiki) by nvk
- Built for [Bob Shell](https://github.com/bob-shell) by the community
- Thanks to all contributors and testers

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bob-llmwiki-knowledge-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bob-llmwiki-knowledge-manager/discussions)
- **Documentation**: See `docs/` directory

---

**Ready to get started?** → [Quick Start Guide](docs/QUICK_START.md) 📚
