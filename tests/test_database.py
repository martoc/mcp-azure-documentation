"""Tests for database operations."""

import tempfile
from pathlib import Path

from mcp_azure_documentation.database import DocumentDatabase
from mcp_azure_documentation.models import Document


def test_database_initialisation() -> None:
    """Test database initialisation creates schema."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)
        assert db.db_path == db_path
        assert db_path.exists()


def test_upsert_document() -> None:
    """Test inserting and updating a document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = Document(
            path="azure-functions/consumption-plan.md",
            title="Consumption plan",
            description="Learn about the Consumption plan",
            section="azure-functions",
            content="Content about the Consumption hosting plan",
            url="https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan",
        )

        db.upsert_document(doc)
        retrieved = db.get_document("azure-functions/consumption-plan.md")

        assert retrieved is not None
        assert retrieved.title == "Consumption plan"
        assert retrieved.content == "Content about the Consumption hosting plan"


def test_upsert_document_update() -> None:
    """Test updating an existing document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="azure-functions/consumption-plan.md",
            title="Original",
            description=None,
            section="azure-functions",
            content="Original content",
            url="https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan",
        )
        db.upsert_document(doc1)

        doc2 = Document(
            path="azure-functions/consumption-plan.md",
            title="Updated",
            description=None,
            section="azure-functions",
            content="Updated content",
            url="https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan",
        )
        db.upsert_document(doc2)

        retrieved = db.get_document("azure-functions/consumption-plan.md")
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "Updated content"


def test_search_documents() -> None:
    """Test searching documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="doc1.md",
            title="Azure Functions Deployments",
            description="Deployment guide",
            section="azure-functions",
            content="This document covers Azure Functions deployment concepts",
            url="https://learn.microsoft.com/en-us/azure/azure-functions/deployment-zip-push",
        )
        doc2 = Document(
            path="doc2.md",
            title="Azure Storage Services",
            description="Services guide",
            section="storage",
            content="This document covers Azure Storage service networking",
            url="https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("deployment")
        assert len(results) > 0
        assert any("Deployment" in r.title for r in results)


def test_search_with_section_filter() -> None:
    """Test searching with section filter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = Document(
            path="doc1.md",
            title="Azure Functions Overview",
            description=None,
            section="azure-functions",
            content="Azure Functions documentation content",
            url="https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview",
        )
        doc2 = Document(
            path="doc2.md",
            title="Azure Storage Overview",
            description=None,
            section="storage",
            content="Azure Storage documentation content",
            url="https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("Azure", section="azure-functions")
        assert len(results) == 1
        assert results[0].section == "azure-functions"


def test_get_document_not_found() -> None:
    """Test getting a non-existent document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        result = db.get_document("nonexistent.md")
        assert result is None


def test_clear_database() -> None:
    """Test clearing all documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = Document(
            path="test.md",
            title="Test",
            description=None,
            section="azure-functions",
            content="Content",
            url="https://learn.microsoft.com/en-us/azure/azure-functions/test",
        )
        db.upsert_document(doc)

        assert db.get_document_count() == 1

        db.clear()

        assert db.get_document_count() == 0


def test_get_document_count() -> None:
    """Test getting document count."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        assert db.get_document_count() == 0

        for i in range(5):
            doc = Document(
                path=f"doc{i}.md",
                title=f"Doc {i}",
                description=None,
                section="azure-functions",
                content=f"Content {i}",
                url=f"https://learn.microsoft.com/en-us/azure/azure-functions/doc{i}",
            )
            db.upsert_document(doc)

        assert db.get_document_count() == 5
