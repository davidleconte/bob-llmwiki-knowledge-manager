"""Tests for document templates."""

from pathlib import Path

import pytest


@pytest.fixture
def templates_dir():
    """Path to templates directory."""
    return Path(__file__).parent.parent / "config" / "templates"


@pytest.fixture
def template_files(templates_dir):
    """List of template files."""
    return list(templates_dir.glob("*.md"))


@pytest.mark.unit
def test_templates_directory_exists(templates_dir):
    """Test that templates directory exists."""
    assert templates_dir.exists(), "Templates directory should exist"
    assert templates_dir.is_dir(), "Templates path should be a directory"


@pytest.mark.unit
def test_required_templates_exist(templates_dir):
    """Test that all required templates exist."""
    required_templates = ["concept.md", "guide.md", "reference.md", "research.md"]

    for template in required_templates:
        template_path = templates_dir / template
        assert template_path.exists(), f"Template {template} should exist"


@pytest.mark.unit
def test_templates_are_markdown(template_files):
    """Test that all templates are markdown files."""
    for template in template_files:
        assert template.suffix == ".md", f"{template.name} should be a markdown file"


@pytest.mark.unit
def test_templates_not_empty(template_files):
    """Test that templates are not empty."""
    for template in template_files:
        content = template.read_text()
        assert len(content) > 0, f"{template.name} should not be empty"
        assert len(content) > 100, f"{template.name} should have substantial content"


@pytest.mark.unit
def test_concept_template_structure():
    """Test concept template has required sections."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "concept.md"
    content = template_path.read_text()

    required_sections = [
        "## Overview",
        "## Key Points",
        "## Details",
        "## Related Documents",
        "## References",
    ]

    for section in required_sections:
        assert section in content, f"Concept template should have '{section}' section"


@pytest.mark.unit
def test_guide_template_structure():
    """Test guide template has required sections."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "guide.md"
    content = template_path.read_text()

    required_sections = [
        "## Overview",
        "## Prerequisites",
        "## Steps",
        "## Troubleshooting",
        "## Related Documents",
    ]

    for section in required_sections:
        assert section in content, f"Guide template should have '{section}' section"


@pytest.mark.unit
def test_reference_template_structure():
    """Test reference template has required sections."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "reference.md"
    content = template_path.read_text()

    required_sections = ["## Overview", "## Related Documents", "## References"]

    for section in required_sections:
        assert section in content, f"Reference template should have '{section}' section"


@pytest.mark.unit
def test_research_template_structure():
    """Test research template has required sections."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "research.md"
    content = template_path.read_text()

    required_sections = [
        "## Objective",
        "## Methodology",
        "## Findings",
        "## Conclusions",
        "## Related Documents",
    ]

    for section in required_sections:
        assert section in content, f"Research template should have '{section}' section"


@pytest.mark.unit
def test_templates_have_placeholders(template_files):
    """Test that templates have placeholder text."""
    for template in template_files:
        content = template.read_text()
        # Templates should have brackets indicating placeholders
        assert "[" in content and "]" in content, (
            f"{template.name} should have placeholder text in brackets"
        )


@pytest.mark.unit
def test_templates_have_related_documents_section(template_files):
    """Test that all templates have Related Documents section."""
    for template in template_files:
        content = template.read_text()
        assert "## Related Documents" in content, (
            f"{template.name} should have Related Documents section"
        )


@pytest.mark.unit
def test_concept_template_has_references():
    """Test that concept template has References section."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "concept.md"
    content = template_path.read_text()
    assert "## References" in content, "Concept template should have References section"


@pytest.mark.unit
def test_research_template_has_metadata():
    """Test that research template has metadata in footer."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "research.md"
    content = template_path.read_text()

    # Check for metadata in footer
    assert "*Last Updated:" in content, "Research template should have Last Updated field"
    assert "*Category:" in content, "Research template should have Category field"


@pytest.mark.unit
def test_guide_template_has_prerequisites():
    """Test that guide template has Prerequisites section."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "guide.md"
    content = template_path.read_text()
    assert "## Prerequisites" in content, "Guide template should have Prerequisites section"


@pytest.mark.unit
def test_guide_template_has_troubleshooting():
    """Test that guide template has Troubleshooting section."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "guide.md"
    content = template_path.read_text()
    assert "## Troubleshooting" in content, "Guide template should have Troubleshooting section"


@pytest.mark.unit
def test_reference_template_has_api_section():
    """Test that reference template has API/Components section."""
    template_path = Path(__file__).parent.parent / "config" / "templates" / "reference.md"
    content = template_path.read_text()
    assert "## API" in content or "Components" in content, (
        "Reference template should have API or Components section"
    )


@pytest.mark.unit
def test_templates_have_footer_metadata(template_files):
    """Test that templates have footer metadata."""
    for template in template_files:
        content = template.read_text()
        assert "*Last Updated:" in content or "Last Updated" in content, (
            f"{template.name} should have Last Updated metadata"
        )
        assert "*Category:" in content or "Category" in content, (
            f"{template.name} should have Category metadata"
        )
