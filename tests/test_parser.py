"""Tests for document parser."""

import tempfile
from pathlib import Path

from mcp_azure_documentation.parser import DocumentParser


def test_extract_section_root() -> None:
    """Test extracting section from root-level file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("index.md"))
    assert section == "root"


def test_extract_section_nested() -> None:
    """Test extracting section from nested file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("azure-functions/consumption-plan.md"))
    assert section == "azure-functions"


def test_compute_url_regular_file() -> None:
    """Test computing documentation URL for a regular file."""
    parser = DocumentParser()
    url = parser._compute_url(Path("azure-functions/consumption-plan.md"))
    assert url == "https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan"


def test_compute_url_index_file() -> None:
    """Test computing URL for an index.md file."""
    parser = DocumentParser()
    url = parser._compute_url(Path("azure-functions/index.md"))
    assert url == "https://learn.microsoft.com/en-us/azure/azure-functions"


def test_compute_url_root_index() -> None:
    """Test computing URL for root index.md."""
    parser = DocumentParser()
    url = parser._compute_url(Path("index.md"))
    assert url == "https://learn.microsoft.com/en-us/azure"


def test_clean_content_removes_docfx_includes() -> None:
    """Test cleaning content removes DocFX INCLUDE directives."""
    parser = DocumentParser()
    content = "Before.\n[!INCLUDE [sample-note](../../includes/sample-note.md)]\nAfter."
    cleaned = parser._clean_content(content)
    assert "[!INCLUDE" not in cleaned
    assert "Before." in cleaned
    assert "After." in cleaned


def test_clean_content_strips_alert_markers() -> None:
    """Test cleaning content strips DocFX alert markers but keeps the text."""
    parser = DocumentParser()
    content = "> [!NOTE]\n> This is a note."
    cleaned = parser._clean_content(content)
    assert "[!NOTE]" not in cleaned
    assert "This is a note." in cleaned


def test_clean_content_removes_zone_pivots() -> None:
    """Test cleaning content removes DocFX zone pivot markers."""
    parser = DocumentParser()
    content = '::: zone pivot="programming-language-csharp"\nC# content.\n::: zone-end'
    cleaned = parser._clean_content(content)
    assert ":::" not in cleaned
    assert "C# content." in cleaned


def test_clean_content_removes_html_comments() -> None:
    """Test cleaning content removes HTML comments."""
    parser = DocumentParser()
    content = "<!-- Comment -->\nContent\n<!-- Another -->"
    cleaned = parser._clean_content(content)
    assert "<!--" not in cleaned
    assert "Content" in cleaned


def test_parse_file_with_frontmatter() -> None:
    """Test parsing a file with YAML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "test.md"

        content = """---
title: Consumption plan
description: Learn about the Consumption hosting plan for Azure Functions
---

# Consumption plan

This is a test.
"""
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path)

        assert doc is not None
        assert doc.title == "Consumption plan"
        assert doc.description == "Learn about the Consumption hosting plan for Azure Functions"
        assert "Consumption plan" in doc.content
        assert doc.path == "test.md"


def test_parse_file_without_frontmatter() -> None:
    """Test parsing a file without YAML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "test-file.md"

        content = "# Test Content\n\nThis is a test."
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path)

        assert doc is not None
        assert doc.title == "Test File"  # Fallback from filename
        assert "Test Content" in doc.content


def test_parse_file_computes_section_and_url() -> None:
    """Test that parsing a nested file computes the correct section and URL."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        service_dir = base_path / "azure-functions"
        service_dir.mkdir()
        file_path = service_dir / "consumption-plan.md"
        file_path.write_text("---\ntitle: Consumption plan\n---\n\nContent.")

        doc = parser.parse_file(file_path, base_path)

        assert doc is not None
        assert doc.section == "azure-functions"
        assert doc.url == "https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan"
