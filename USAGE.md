# Usage Guide

This guide provides detailed instructions for using the MCP Azure Documentation Server.

## Installation

### Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Docker (optional, for containerised deployment)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:martoc/mcp-azure-documentation.git
   cd mcp-azure-documentation
   ```

2. Initialise the development environment:
   ```bash
   make init
   ```

3. Build the documentation index:
   ```bash
   make index
   ```

## Indexing Documentation

### Initial Indexing

Index the Azure documentation from the main branch:

```bash
uv run azure-docs-index index
```

### Rebuilding the Index

Clear the existing index and rebuild from scratch:

```bash
uv run azure-docs-index index --rebuild
```

### Indexing a Specific Branch

Index documentation from a specific Git branch:

```bash
uv run azure-docs-index index --branch main
```

### Index Statistics

View the number of indexed documents:

```bash
uv run azure-docs-index stats
```

## Running the MCP Server

### Using the Container Image (Recommended)

The `martoc/mcp-azure-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-azure-documentation:latest
```

### Local Development

Run the server directly using uv:

```bash
make run
# or
uv run mcp-azure-documentation
```

### Building a Local Docker Image

Build and run the server in a Docker container:

```bash
make docker-build
make docker-run
```

## MCP Client Configuration

### Claude Code (Container Image)

Add to your project's `.mcp.json` to use the published container image:

```json
{
  "mcpServers": {
    "azure-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-azure-documentation:latest"]
    }
  }
}
```

### Claude Code (Local Development)

Add to your project's `.mcp.json` for local development:

```json
{
  "mcpServers": {
    "azure-documentation": {
      "command": "uv",
      "args": ["run", "mcp-azure-documentation"],
      "cwd": "/path/to/mcp-azure-documentation"
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "azure-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-azure-documentation:latest"]
    }
  }
}
```

## Using the Tools

### Searching Documentation

Search for topics in Azure documentation:

```
Search for "consumption plan"
Search for "blob storage tiers" in section "storage"
Search for "virtual network peering" with limit 20
```

Example response:
```json
{
  "query": "consumption plan",
  "section_filter": null,
  "result_count": 5,
  "results": [
    {
      "title": "Consumption plan",
      "url": "https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan",
      "path": "azure-functions/consumption-plan.md",
      "section": "azure-functions",
      "snippet": "...the <mark>Consumption</mark> <mark>plan</mark> scales dynamically...",
      "relevance_score": 12.5432
    }
  ]
}
```

### Reading Documentation

Retrieve the full content of a specific page:

```
Read documentation at path "azure-functions/consumption-plan.md"
```

Example response:
```json
{
  "path": "azure-functions/consumption-plan.md",
  "title": "Consumption plan",
  "description": "Learn about the Consumption hosting plan for Azure Functions",
  "section": "azure-functions",
  "url": "https://learn.microsoft.com/en-us/azure/azure-functions/consumption-plan",
  "content": "# Consumption plan\n\n..."
}
```

## Common Sections

Azure documentation is organised by service or product, one top-level directory per service under `articles/` in the source repository. Common sections include:

- **azure-functions**: Azure Functions
- **app-service**: Azure App Service
- **storage**: Azure Storage
- **virtual-machines**: Azure Virtual Machines
- **aks**: Azure Kubernetes Service
- **azure-sql**: Azure SQL
- **cosmos-db**: Azure Cosmos DB
- **active-directory**: Microsoft Entra ID (Azure Active Directory)
- **azure-monitor**: Azure Monitor

Use these section names with the `section` parameter to filter search results.

## Development Workflow

### Code Quality Checks

Run all code quality checks:

```bash
make build
```

This runs:
- Linter (ruff)
- Type checker (mypy)
- Tests with coverage (pytest)

### Individual Checks

```bash
make lint       # Run linter only
make typecheck  # Run type checker only
make test       # Run tests only
make format     # Format code
```

### Updating Dependencies

Update the lock file:

```bash
make generate
```

## Troubleshooting

### Index Build Fails

If the index build fails, try:

1. Check your internet connection
2. Verify Git is installed and accessible
3. Try rebuilding with a different branch:
   ```bash
   uv run azure-docs-index index --rebuild --branch main
   ```

### No Search Results

If searches return no results:

1. Verify the index is built:
   ```bash
   uv run azure-docs-index stats
   ```

2. Rebuild the index if necessary:
   ```bash
   uv run azure-docs-index index --rebuild
   ```

### Database Location

The default database location is `data/azure_docs.db`. To use a custom location:

```bash
uv run azure-docs-index index --database /path/to/custom.db
```

## Performance Considerations

- **Initial indexing**: May take a while given the size of the azure-docs repository (~15,000 markdown files)
- **Sparse checkout**: Only `articles/` is cloned, reducing download size significantly
- **Search performance**: FTS5 with BM25 ranking provides fast, relevant results
- **Memory usage**: Minimal during operation; database is SQLite-based
