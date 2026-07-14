"""Tests for mode configuration."""
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def mode_config_path():
    """Path to the mode configuration file."""
    return Path(__file__).parent.parent / "config" / "custom_modes.yaml"


@pytest.fixture
def mode_config(mode_config_path):
    """Load mode configuration."""
    with open(mode_config_path, 'r') as f:
        return yaml.safe_load(f)


@pytest.mark.unit
def test_mode_config_exists(mode_config_path):
    """Test that mode configuration file exists."""
    assert mode_config_path.exists(), "Mode configuration file should exist"


@pytest.mark.unit
def test_mode_config_valid_yaml(mode_config_path):
    """Test that mode configuration is valid YAML."""
    with open(mode_config_path, 'r') as f:
        config = yaml.safe_load(f)
    assert config is not None, "Configuration should be valid YAML"


@pytest.mark.unit
def test_mode_config_has_custom_modes(mode_config):
    """Test that configuration has customModes key."""
    assert 'customModes' in mode_config, "Configuration should have customModes"
    assert isinstance(mode_config['customModes'], list), "customModes should be a list"
    assert len(mode_config['customModes']) > 0, "Should have at least one mode"


@pytest.mark.unit
def test_knowledge_manager_mode_exists(mode_config):
    """Test that knowledge-manager mode exists."""
    modes = mode_config['customModes']
    km_mode = next((m for m in modes if m.get('slug') == 'knowledge-manager'), None)
    assert km_mode is not None, "knowledge-manager mode should exist"


@pytest.mark.unit
def test_knowledge_manager_mode_structure(mode_config):
    """Test that knowledge-manager mode has required fields."""
    modes = mode_config['customModes']
    km_mode = next((m for m in modes if m.get('slug') == 'knowledge-manager'), None)

    assert 'slug' in km_mode, "Mode should have slug"
    assert 'name' in km_mode, "Mode should have name"
    assert 'roleDefinition' in km_mode, "Mode should have roleDefinition"
    assert 'customInstructions' in km_mode, "Mode should have customInstructions"

    assert km_mode['slug'] == 'knowledge-manager', "Slug should be knowledge-manager"
    assert '📚' in km_mode['name'], "Name should include emoji"


@pytest.mark.unit
def test_mode_role_definition_content(mode_config):
    """Test that role definition contains expected content."""
    modes = mode_config['customModes']
    km_mode = next((m for m in modes if m.get('slug') == 'knowledge-manager'), None)

    role_def = km_mode['roleDefinition']
    assert 'knowledge' in role_def.lower(), "Should mention knowledge"
    assert 'document' in role_def.lower(), "Should mention documentation"


@pytest.mark.unit
def test_mode_custom_instructions_content(mode_config):
    """Test that custom instructions contain expected sections."""
    modes = mode_config['customModes']
    km_mode = next((m for m in modes if m.get('slug') == 'knowledge-manager'), None)

    instructions = km_mode['customInstructions']

    # Check for key sections (flexible matching)
    assert 'concept' in instructions.lower(), "Should mention concepts"
    assert 'guide' in instructions.lower(), "Should mention guides"
    assert 'reference' in instructions.lower(), "Should mention references"
    assert 'research' in instructions.lower(), "Should mention research"


@pytest.mark.unit
def test_mode_mentions_templates(mode_config):
    """Test that mode mentions document templates."""
    modes = mode_config['customModes']
    km_mode = next((m for m in modes if m.get('slug') == 'knowledge-manager'), None)

    instructions = km_mode['customInstructions']
    assert 'template' in instructions.lower(), "Should mention templates"


@pytest.mark.unit
def test_mode_mentions_save_memory(mode_config):
    """Test that mode mentions save_memory tool."""
    modes = mode_config['customModes']
    km_mode = next((m for m in modes if m.get('slug') == 'knowledge-manager'), None)

    instructions = km_mode['customInstructions']
    assert 'save_memory' in instructions or 'memory' in instructions.lower(), \
        "Should mention memory persistence"


@pytest.mark.unit
def test_mode_has_file_groups(mode_config):
    """Test that mode has file access groups."""
    modes = mode_config['customModes']
    km_mode = next((m for m in modes if m.get('slug') == 'knowledge-manager'), None)

    assert 'groups' in km_mode, "Mode should have groups"
    groups = km_mode['groups']
    assert isinstance(groups, list), "Groups should be a list"

    # Check for markdown file editing capability
    has_edit = any('edit' in str(g).lower() for g in groups)
    assert has_edit, "Should have edit capability"
