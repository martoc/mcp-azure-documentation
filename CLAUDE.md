# Claude Code Instructions

This file contains instructions for Claude Code when working with the MCP Azure Documentation Server codebase.

## Project Overview

This is an MCP (Model Context Protocol) server that provides search and retrieval tools for Azure documentation. It uses:
- FastMCP for the MCP server framework
- SQLite FTS5 for full-text search with BM25 ranking
- Python-frontmatter for parsing markdown files with YAML frontmatter
- Sparse Git checkout for efficient cloning of the `articles` directory from `MicrosoftDocs/azure-docs`

## Code Principles

### British English
- Use British English in all code, comments, and documentation
- Examples: "initialise" not "initialize", "colour" not "color"

### Type Safety
- All functions must have type hints
- Use modern union syntax: `str | None` instead of `Optional[str]`
- Run mypy in strict mode before committing

### Error Handling
- Use explicit error handling
- Raise appropriate exceptions with descriptive messages
- Never silently fail

### Code Style
- Follow PEP 8 guidelines
- Maximum line length: 120 characters
- Use ruff for linting and formatting
- See CODESTYLE.md for detailed style guidelines

## Development Workflow

### Making Changes

1. **Before starting**:
   - Ensure development environment is initialised: `make init`
   - Understand the existing code structure

2. **During development**:
   - Write tests for new functionality
   - Update type hints as needed
   - Add docstrings following Google style

3. **Before committing**:
   - Format code: `make format`
   - Run linter: `make lint`
   - Run type checker: `make typecheck`
   - Run tests: `make test`
   - Or run all checks: `make build`

### Testing

- Write tests using pytest
- Place tests in `tests/` directory
- Mirror source structure in test files
- Test both success and failure cases
- Aim for high coverage (>80%)

### Common Tasks

#### Adding a New Feature

1. Update the relevant model in `models.py` if needed
2. Implement the feature in the appropriate module
3. Add corresponding tests
4. Update documentation
5. Run `make build` to verify all checks pass

#### Modifying the Parser

When modifying `parser.py`:
- Consider Azure docs' documentation structure (DocFX-based)
- Update URL computation if needed
- Handle DocFX syntax (e.g., `[!INCLUDE]` directives, `[!NOTE]`/`[!TIP]`/`[!WARNING]` alert markers, `::: zone` pivots)
- Test frontmatter parsing for title and description fields

#### Updating Dependencies

1. Modify `pyproject.toml`
2. Run `make generate` to update lock file
3. Test thoroughly
4. Document the reason for the dependency

#### Indexer Modifications

When modifying `indexer.py`:
- Consider network efficiency (sparse checkout)
- Handle Git operations safely
- Log progress appropriately
- Test with different branches
- The `azure-docs` repository is large (~15,000 markdown files); keep the sparse checkout limited to `articles`

## Project Structure

```
mcp-azure-documentation/
├── src/mcp_azure_documentation/
│   ├── __init__.py         # Package initialisation
│   ├── models.py           # Data models (Document, SearchResult, etc.)
│   ├── database.py         # SQLite FTS5 database operations
│   ├── parser.py           # Markdown file parser
│   ├── indexer.py          # Documentation indexer
│   ├── server.py           # FastMCP server implementation
│   └── cli.py              # Command-line interface
├── tests/                  # Test files
├── data/                   # SQLite database storage
├── pyproject.toml          # Project configuration
├── Makefile                # Build automation
├── Dockerfile              # Container configuration
└── README.md               # Project documentation
```

## MCP Tools

The server exposes two MCP tools:

1. **search_documentation**: Full-text search with optional section filtering
2. **read_documentation**: Retrieve complete document content

Both tools return JSON-formatted responses.

## Database Schema

The database has two main tables:
- `documents`: Main document storage
- `documents_fts`: FTS5 virtual table for search

Triggers keep the FTS index synchronised with the main table.

## Common Patterns

### Database Operations
Always use the context manager pattern:
```python
with self._get_connection() as conn:
    # Perform operations
    conn.commit()
```

### Lazy Initialisation
The server uses lazy initialisation for the database:
```python
_database: DocumentDatabase | None = None

def get_database() -> DocumentDatabase:
    global _database
    if _database is None:
        _database = DocumentDatabase(db_path)
    return _database
```

### Error Messages
Provide helpful error messages with suggestions:
```python
return json.dumps({
    "error": f"Document not found: {path}",
    "suggestion": "Use search_documentation to find valid document paths.",
})
```

## Debugging

### Index Issues
If the index isn't working correctly:
1. Check index statistics: `uv run azure-docs-index stats`
2. Rebuild the index: `uv run azure-docs-index index --rebuild`
3. Check database file permissions
4. Verify Git clone succeeded

### Search Not Finding Results
1. Verify stemming is working (Porter stemmer)
2. Check BM25 scoring weights
3. Examine the FTS5 query syntax
4. Test with simpler queries

### Docker Build Failures
1. Ensure Git is available in the container
2. Check network connectivity during build
3. Verify sparse checkout configuration
4. Check uv installation

## Container Image

The `martoc/mcp-azure-documentation` container image is published to Docker Hub with the documentation index pre-built.

- **Image**: `martoc/mcp-azure-documentation`
- **Platforms**: `linux/amd64`, `linux/arm64`
- **CI/CD**: Built and published automatically via GitHub Actions on push to `main`
- **Index**: Pre-built at image build time from `MicrosoftDocs/azure-docs` `main` branch

## Documentation URLs

Azure documentation URL pattern:
```
https://learn.microsoft.com/en-us/azure/{path}
```

The parser removes `.md` extensions and handles `index.md` files when computing URLs.

## DocFX Syntax Cleaning

The parser handles DocFX-specific content:
- `[!INCLUDE [name](path)]` directives: removed (the included content is not indexed)
- `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]` alert markers: stripped, keeping the surrounding blockquote text
- `::: zone pivot="..."` / `::: zone-end` lines: removed
- HTML comments and tags: removed

## Git Operations

The indexer uses sparse checkout to clone a single directory:
```bash
git clone --depth 1 --filter=blob:none --sparse --branch main https://github.com/MicrosoftDocs/azure-docs.git
git sparse-checkout set articles
```

This significantly reduces clone time and disk usage given the size of the azure-docs repository.

## Performance Considerations

- **SQLite FTS5**: Provides fast full-text search with BM25 ranking
- **Sparse checkout**: Reduces clone size by fetching only the `articles` directory
- **Lazy loading**: Database initialised only when needed
- **Connection pooling**: Not needed for SQLite (file-based)

## Maintenance

### Updating to New Azure Documentation

1. Update the branch in indexer if needed
2. Rebuild the index: `uv run azure-docs-index index --rebuild --branch main`
3. Test search functionality

### Monitoring Index Health

Regularly check:
- Document count: `uv run azure-docs-index stats`
- Search result quality
- Database file size
- Query performance

## Troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Run `make init` to sync dependencies
- Check Python version (requires 3.12+)

### Type Check Failures
- Review mypy output carefully
- Update type hints as needed
- Check for missing return type annotations

### Test Failures
- Review test output for details
- Check test database setup
- Verify fixtures are correct
- Run with verbose output: `pytest -vvv`

## Best Practices

1. **Never** commit without running `make build`
2. **Always** write tests for new features
3. **Keep** functions focused and single-purpose
4. **Use** type hints consistently
5. **Document** non-obvious behaviour
6. **Follow** British English spelling
7. **Update** documentation when changing behaviour
8. **Test** with different azure-docs branches
