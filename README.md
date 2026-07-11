# Bob Shell Knowledge Manager

A reusable knowledge management framework for Bob Shell, inspired by LLM-Wiki but built on Bob Shell's native capabilities.

## Features

- Structured Knowledge Base - Organized into concepts, guides, references, and research
- Full-Text Search - Search across all documents with context
- Persistent Memory - Save key facts with Bob Shell's save_memory tool
- Automatic Cross-Referencing - Maintain bidirectional links between documents
- Document Templates - Consistent structure for all document types
- Custom Bob Shell Mode - Optimized behavior for knowledge management
- Zero External Dependencies - Uses only Bob Shell's native features

## Quick Start

Installation:
bash
cd ~/Projects
git clone https://github.com/yourusername/bob-llmwiki-knowledge-manager.git
cd bob-llmwiki-knowledge-manager
./scripts/install.sh


Initialize in your project:
bash
cd ~/Projects/your-project
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh


Start using:
bash
bob --chat-mode=knowledge-manager


## Documentation

- Installation Guide: docs/INSTALLATION.md
- Usage Guide: docs/USAGE.md
- Customization: docs/CUSTOMIZATION.md
- Workflows: docs/WORKFLOWS.md
- Architecture: docs/ARCHITECTURE.md

## License

MIT License - see LICENSE file

## Acknowledgments

- Inspired by LLM-Wiki by nvk
- Built for Bob Shell

Made with love for the Bob Shell community
