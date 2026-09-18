"""Parser for Azure documentation markdown files."""

import re
from pathlib import Path

import frontmatter

from mcp_azure_documentation.models import Document, DocumentMetadata


class DocumentParser:
    """Parses markdown files with YAML frontmatter from the azure-docs repository."""

    AZURE_DOCS_BASE_URL = "https://learn.microsoft.com/en-us/azure"

    def parse_file(self, file_path: Path, base_path: Path) -> Document | None:
        """Parse a markdown file and extract metadata and content.

        Args:
            file_path: Path to the markdown file.
            base_path: Base path of the documentation directory.

        Returns:
            Document instance or None if parsing fails.
        """
        try:
            post = frontmatter.load(file_path)
            metadata = self._extract_metadata(post.metadata, file_path)
            relative_path = file_path.relative_to(base_path)
            section = self._extract_section(relative_path)
            url = self._compute_url(relative_path)
            content = self._clean_content(post.content)

            return Document(
                path=str(relative_path),
                title=metadata.title,
                description=metadata.description,
                section=section,
                content=content,
                url=url,
            )
        except Exception:  # noqa: BLE001 (skip malformed docs during bulk indexing rather than aborting)
            return None

    def _extract_metadata(self, metadata: dict[str, object], file_path: Path) -> DocumentMetadata:
        """Extract structured metadata from frontmatter.

        Args:
            metadata: Dictionary of frontmatter fields.
            file_path: Path to the file for fallback title extraction.

        Returns:
            DocumentMetadata instance.
        """
        title = metadata.get("title")
        if not isinstance(title, str):
            # Fallback to filename if no title in frontmatter
            title = file_path.stem.replace("-", " ").replace("_", " ").title()

        description = metadata.get("description")
        if not isinstance(description, str):
            description = None

        return DocumentMetadata(
            title=title,
            description=description,
        )

    def _extract_section(self, relative_path: Path) -> str:
        """Extract the top-level Azure service/product from the path.

        Args:
            relative_path: Path relative to the articles directory.

        Returns:
            Section name (first directory component, e.g. 'azure-functions', or 'root').
        """
        parts = relative_path.parts
        return parts[0] if len(parts) > 1 else "root"

    def _compute_url(self, relative_path: Path) -> str:
        """Compute the learn.microsoft.com documentation URL.

        Args:
            relative_path: Path relative to the articles directory.

        Returns:
            Full URL to the documentation page.
        """
        path_str = str(relative_path)
        # Remove .md extension
        path_str = re.sub(r"\.md$", "", path_str)
        # Handle index pages
        path_str = re.sub(r"/index$", "", path_str)
        if path_str == "index":
            path_str = ""

        if path_str:
            return f"{self.AZURE_DOCS_BASE_URL}/{path_str}"
        return self.AZURE_DOCS_BASE_URL

    def _clean_content(self, content: str) -> str:
        """Clean markdown content for indexing.

        Removes DocFX-specific syntax and other markup artifacts.

        Args:
            content: Raw markdown content.

        Returns:
            Cleaned content suitable for indexing.
        """
        # Remove DocFX [!INCLUDE [name](path)] directives
        content = re.sub(r"\[!INCLUDE\s*\[[^\]]*\]\([^)]*\)\]", "", content)
        # Strip DocFX alert type markers, keeping the surrounding blockquote text
        content = re.sub(r"\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", "", content)
        # Remove DocFX zone pivot lines ("::: zone pivot=..." / "::: zone-end")
        content = re.sub(r"^:::.*$\n?", "", content, flags=re.MULTILINE)
        # Remove HTML comments
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)
        return content.strip()
