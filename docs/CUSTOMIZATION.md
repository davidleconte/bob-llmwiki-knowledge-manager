# Customization Guide

This guide covers how to customize Bob Shell Knowledge Manager for your specific needs.

## Overview

Bob Shell Knowledge Manager can be customized in several ways:

1. Mode Configuration - Modify the knowledge-manager mode behavior
2. Document Templates - Customize document structure
3. Directory Structure - Adapt the knowledge base organization
4. Project-Specific Rules - Add custom instructions per project

## Customizing the Mode

### Location

The mode configuration is stored in:
- System-wide: ~/.bob/custom_modes.yaml
- Project-specific: .bob/custom_modes.yaml (overrides system-wide)

### Basic Customization

Edit ~/.bob/custom_modes.yaml to modify:
- Display name
- Role definition
- Custom instructions
- Naming conventions
- Quality standards

### Project-Specific Mode

Create .bob/custom_modes.yaml in your project for project-specific customization.

## Customizing Templates

Templates are in: ~/Projects/bob-llmwiki-knowledge-manager/config/templates/

Modify existing templates or create new ones to match your needs.

## Customizing Directory Structure

Adapt the knowledge base organization:
- Flat structure for smaller projects
- Domain-driven structure for larger projects
- Custom categories for specific needs

## Integration with Other Tools

- Obsidian compatibility
- VS Code snippets
- Git hooks for validation

## Team Customization

Store team configuration in .bob/custom_modes.yaml (committed to git).
Individual developers can override in ~/.bob/custom_modes.yaml.

## Next Steps

- Usage Examples: See Usage Guide
- Workflows: See Workflows Guide
- Architecture: See Architecture Guide
