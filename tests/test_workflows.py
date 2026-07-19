"""Tests for workflow scripts and integration."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Path to project root."""
    return Path(__file__).parent.parent


@pytest.fixture
def scripts_dir(project_root):
    """Path to scripts directory."""
    return project_root / "scripts"


@pytest.mark.unit
def test_scripts_directory_exists(scripts_dir):
    """Test that scripts directory exists."""
    assert scripts_dir.exists(), "Scripts directory should exist"
    assert scripts_dir.is_dir(), "Scripts path should be a directory"


@pytest.mark.unit
def test_required_scripts_exist(scripts_dir):
    """Test that all required scripts exist."""
    required_scripts = ["install.sh", "init-project.sh", "validate-kb.sh", "export-kb.sh"]

    for script in required_scripts:
        script_path = scripts_dir / script
        assert script_path.exists(), f"Script {script} should exist"


@pytest.mark.unit
def test_scripts_are_executable(scripts_dir):
    """Test that scripts are executable."""
    scripts = ["install.sh", "init-project.sh", "validate-kb.sh", "export-kb.sh"]

    for script in scripts:
        script_path = scripts_dir / script
        assert script_path.stat().st_mode & 0o111, f"{script} should be executable"


@pytest.mark.unit
def test_scripts_have_shebang(scripts_dir):
    """Test that scripts have proper shebang."""
    scripts = ["install.sh", "init-project.sh", "validate-kb.sh", "export-kb.sh"]

    for script in scripts:
        script_path = scripts_dir / script
        with open(script_path, "r") as f:
            first_line = f.readline()
        assert first_line.startswith("#!/bin/bash"), f"{script} should have bash shebang"


@pytest.mark.unit
def test_install_script_checks_bob_shell(scripts_dir):
    """Test that install script checks for Bob Shell."""
    script_path = scripts_dir / "install.sh"
    content = script_path.read_text()

    assert ".bob" in content or "bob" in content.lower(), (
        "Install script should check for Bob Shell"
    )


@pytest.mark.unit
def test_init_project_script_creates_structure(scripts_dir):
    """Test that init-project script creates KB structure."""
    script_path = scripts_dir / "init-project.sh"
    content = script_path.read_text()

    required_dirs = ["concepts", "guides", "references", "research"]
    for dir_name in required_dirs:
        assert dir_name in content, f"Init script should create {dir_name} directory"


@pytest.mark.unit
def test_validate_script_checks_structure(scripts_dir):
    """Test that validate script checks KB structure."""
    script_path = scripts_dir / "validate-kb.sh"
    content = script_path.read_text()

    assert "index.md" in content, "Validate script should check for index.md"
    assert "concepts" in content, "Validate script should check concepts directory"


@pytest.mark.unit
def test_export_script_supports_formats(scripts_dir):
    """Test that export script supports multiple formats."""
    script_path = scripts_dir / "export-kb.sh"
    content = script_path.read_text()

    formats = ["markdown", "obsidian", "html", "pdf"]
    for fmt in formats:
        assert fmt in content, f"Export script should support {fmt} format"


@pytest.mark.integration
def test_install_script_syntax():
    """Test that install script has valid bash syntax."""
    script_path = Path(__file__).parent.parent / "scripts" / "install.sh"
    result = subprocess.run(["bash", "-n", str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Install script has syntax errors: {result.stderr}"


@pytest.mark.integration
def test_init_project_script_syntax():
    """Test that init-project script has valid bash syntax."""
    script_path = Path(__file__).parent.parent / "scripts" / "init-project.sh"
    result = subprocess.run(["bash", "-n", str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Init-project script has syntax errors: {result.stderr}"


@pytest.mark.integration
def test_validate_script_syntax():
    """Test that validate script has valid bash syntax."""
    script_path = Path(__file__).parent.parent / "scripts" / "validate-kb.sh"
    result = subprocess.run(["bash", "-n", str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Validate script has syntax errors: {result.stderr}"


@pytest.mark.integration
def test_export_script_syntax():
    """Test that export script has valid bash syntax."""
    script_path = Path(__file__).parent.parent / "scripts" / "export-kb.sh"
    result = subprocess.run(["bash", "-n", str(script_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Export script has syntax errors: {result.stderr}"


@pytest.mark.unit
def test_examples_directory_exists(project_root):
    """Test that examples directory exists."""
    examples_dir = project_root / "examples"
    assert examples_dir.exists(), "Examples directory should exist"


@pytest.mark.unit
def test_required_examples_exist(project_root):
    """Test that all required examples exist."""
    examples_dir = project_root / "examples"
    required_examples = ["software-project", "research-project", "personal-wiki"]

    for example in required_examples:
        example_path = examples_dir / example
        assert example_path.exists(), f"Example {example} should exist"


@pytest.mark.unit
def test_examples_have_readme(project_root):
    """Test that each example has a README."""
    examples_dir = project_root / "examples"
    examples = ["software-project", "research-project", "personal-wiki"]

    for example in examples:
        readme_path = examples_dir / example / "README.md"
        assert readme_path.exists(), f"Example {example} should have README.md"


@pytest.mark.unit
def test_examples_have_kb_structure(project_root):
    """Test that each example has proper KB structure."""
    examples_dir = project_root / "examples"
    examples = ["software-project", "research-project", "personal-wiki"]

    for example in examples:
        kb_path = examples_dir / example / "docs" / "knowledge-base"
        assert kb_path.exists(), f"Example {example} should have knowledge-base directory"

        # Check for required subdirectories
        for subdir in ["concepts", "guides", "references", "research"]:
            subdir_path = kb_path / subdir
            assert subdir_path.exists(), f"Example {example} should have {subdir} directory"

        # Check for index.md
        index_path = kb_path / "index.md"
        assert index_path.exists(), f"Example {example} should have index.md"


@pytest.mark.unit
def test_documentation_files_exist(project_root):
    """Test that all documentation files exist."""
    docs_dir = project_root / "docs"
    # Live Diátaxis-spine and reference docs at docs/ root.
    # Git-tracked canonical names are UPPERCASE on this project.
    required_docs = [
        "INSTALLATION.md",
        "USAGE.md",
        "CUSTOMIZATION.md",
        "WORKFLOWS.md",
    ]
    for doc in required_docs:
        doc_path = docs_dir / doc
        assert doc_path.exists(), f"Documentation {doc} should exist"

    # ARCHITECTURE.md was moved to docs/kb-manager/ in Sub-Task 7 to avoid
    # the dual-architecture-doc confusion identified in the gap-fix audit.
    assert (docs_dir / "kb-manager" / "ARCHITECTURE.md").exists(), (
        "ARCHITECTURE.md should exist under docs/kb-manager/"
    )

    # COMPARISON.md was moved to docs/archive/ when the docs/ root was curated.
    assert (docs_dir / "archive" / "COMPARISON.md").exists(), (
        "COMPARISON.md should exist under docs/archive/"
    )


@pytest.mark.unit
def test_core_files_exist(project_root):
    """Test that core project files exist."""
    core_files = ["README.md", "LICENSE", "CHANGELOG.md", ".gitignore"]

    for file in core_files:
        file_path = project_root / file
        assert file_path.exists(), f"Core file {file} should exist"


@pytest.mark.unit
def test_config_files_exist(project_root):
    """Test that configuration files exist."""
    config_dir = project_root / "config"
    config_files = ["custom_modes.yaml", "settings.json"]

    for file in config_files:
        file_path = config_dir / file
        assert file_path.exists(), f"Config file {file} should exist"
