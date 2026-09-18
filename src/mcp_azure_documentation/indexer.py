"""Indexer for Azure documentation from the MicrosoftDocs/azure-docs repository."""

import logging
import subprocess
import tempfile
from pathlib import Path

from mcp_azure_documentation.database import DocumentDatabase
from mcp_azure_documentation.parser import DocumentParser

logger = logging.getLogger(__name__)


class AzureDocsIndexer:
    """Indexes Azure documentation from the MicrosoftDocs/azure-docs GitHub repository."""

    AZURE_DOCS_REPO = "https://github.com/MicrosoftDocs/azure-docs.git"
    CONTENT_PATH = "articles"

    def __init__(self, database: DocumentDatabase) -> None:
        """Initialise indexer with database instance.

        Args:
            database: DocumentDatabase instance for storing documents.
        """
        self.database = database
        self.parser = DocumentParser()

    def index_from_git(self, branch: str = "main", shallow: bool = True) -> int:
        """Clone the azure-docs repo and index documentation.

        Args:
            branch: Git branch to clone.
            shallow: Whether to do a shallow clone.

        Returns:
            Number of documents indexed.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "azure-docs"
            self._clone_repository(repo_path, branch, shallow)
            return self._index_directory(repo_path)

    def index_from_path(self, docs_path: Path) -> int:
        """Index documentation from a local path.

        Args:
            docs_path: Path to the repository root directory.

        Returns:
            Number of documents indexed.
        """
        return self._index_directory(docs_path)

    def _clone_repository(self, target_path: Path, branch: str, shallow: bool) -> None:
        """Clone the azure-docs repository.

        Args:
            target_path: Directory to clone into.
            branch: Git branch to clone.
            shallow: Whether to do a shallow clone.
        """
        cmd = ["git", "clone"]
        if shallow:
            cmd.extend(["--depth", "1", "--filter=blob:none", "--sparse"])
        cmd.extend(["--branch", branch, self.AZURE_DOCS_REPO, str(target_path)])

        logger.info("Cloning azure-docs repository...")
        subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603

        # For sparse checkout, only the articles directory holds documentation content
        if shallow:
            logger.info("Setting up sparse checkout for the articles directory...")
            subprocess.run(  # noqa: S603
                ["git", "-C", str(target_path), "sparse-checkout", "set", self.CONTENT_PATH],  # noqa: S607
                check=True,
                capture_output=True,
            )

        logger.info("Repository cloned successfully")

    def _index_directory(self, repo_path: Path) -> int:
        """Index all documentation files in the repository.

        Args:
            repo_path: Path to the repository root.

        Returns:
            Number of documents indexed.

        Raises:
            ValueError: If the content path does not exist.
        """
        content_path = repo_path / self.CONTENT_PATH
        if not content_path.exists():
            msg = f"Content path does not exist: {content_path}"
            raise ValueError(msg)

        indexed_count = self._index_markdown_files(content_path)
        logger.info("Successfully indexed %d documents in total", indexed_count)
        return indexed_count

    def _index_markdown_files(self, content_path: Path) -> int:
        """Index markdown files from the articles directory.

        Args:
            content_path: Path to the articles directory.

        Returns:
            Number of markdown documents indexed.
        """
        md_files = list(content_path.rglob("*.md"))
        logger.info("Found %d markdown files to index", len(md_files))

        indexed_count = 0
        for file_path in md_files:
            document = self.parser.parse_file(file_path, content_path)
            if document:
                self.database.upsert_document(document)
                indexed_count += 1
                logger.debug("Indexed: %s", document.path)
            else:
                logger.warning("Failed to parse: %s", file_path)

        logger.info("Indexed %d markdown documents", indexed_count)
        return indexed_count

    def rebuild_index(self, branch: str = "main") -> int:
        """Clear existing index and rebuild from scratch.

        Args:
            branch: Git branch to index from.

        Returns:
            Number of documents indexed.
        """
        logger.info("Clearing existing index...")
        self.database.clear()
        return self.index_from_git(branch)
