"""Tests for data models."""

from mcp_azure_documentation.models import Document, DocumentMetadata, SearchResult


def test_document_metadata_creation() -> None:
    """Test creating a DocumentMetadata instance."""
    metadata = DocumentMetadata(
        title="Consumption plan",
        description="Learn about the Consumption hosting plan for Azure Functions",
    )
    assert metadata.title == "Consumption plan"
    assert metadata.description == "Learn about the Consumption hosting plan for Azure Functions"


def test_document_metadata_optional_fields() -> None:
    """Test DocumentMetadata with optional fields."""
    metadata = DocumentMetadata(title="Consumption plan")
    assert metadata.title == "Consumption plan"
    assert metadata.description is None


def test_document_creation() -> None:
    """Test creating a Document instance."""
    doc = Document(
        path="azure-functions/consumption-plan.md",
        title="Consumption plan",
        description="Learn about the Consumption hosting plan for Azure Functions",
        section="azure-functions",
        content="# Consumption plan\n\nContent here",
        url="https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan",
    )
    assert doc.path == "azure-functions/consumption-plan.md"
    assert doc.title == "Consumption plan"
    assert doc.section == "azure-functions"
    assert "Content here" in doc.content


def test_search_result_creation() -> None:
    """Test creating a SearchResult instance."""
    result = SearchResult(
        path="azure-functions/consumption-plan.md",
        title="Consumption plan",
        url="https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan",
        snippet="...the Consumption plan scales...",
        score=12.5,
        section="azure-functions",
    )
    assert result.path == "azure-functions/consumption-plan.md"
    assert result.score == 12.5
    assert result.section == "azure-functions"
