[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)

# MCP Azure Documentation Server

An MCP (Model Context Protocol) server that provides search and retrieval tools for [Azure](https://learn.microsoft.com/en-us/azure/) documentation. This server enables AI assistants like Claude to search and read Azure documentation directly from the [MicrosoftDocs/azure-docs](https://github.com/MicrosoftDocs/azure-docs) repository.

## Features

- **Full-text search** using SQLite FTS5 with BM25 ranking and Porter stemming
- **Section filtering** to narrow search results by Azure service or product (e.g. `azure-functions`, `storage`, `app-service`)
- **Sparse checkout** for efficient cloning of only the `articles` directory from azure-docs
- **Docker support** for portable deployment across projects
- **STDIO transport** for seamless MCP client integration

## Quick Start

### Using the Container Image (Recommended)

The `martoc/mcp-azure-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-azure-documentation:latest
```

### Building Locally with Docker

```bash
# Build the Docker image (includes pre-indexed documentation)
make docker-build

# Test the server
make docker-run
```

### Using uv (Local Development)

```bash
# Initialise the environment
make init

# Build the documentation index
make index

# Run the server
make run
```

## Container Image

The `martoc/mcp-azure-documentation` container image is published to [Docker Hub](https://hub.docker.com/r/martoc/mcp-azure-documentation). It includes the pre-built documentation index so the server is ready to use immediately.

| Property | Value |
|----------|-------|
| Registry | Docker Hub |
| Image | `martoc/mcp-azure-documentation` |
| Platforms | `linux/amd64`, `linux/arm64` |
| Base image | `python:3.12-slim` |
| Index | Pre-built at image build time from `MicrosoftDocs/azure-docs` `main` branch |

```bash
# Pull the latest image
docker pull martoc/mcp-azure-documentation:latest

# Run the MCP server
docker run -i --rm martoc/mcp-azure-documentation:latest
```

## Configuration

### Claude Code / Claude Desktop

Add to your `.mcp.json` or global settings to use the published container image:

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

For a locally built Docker image:

```json
{
  "mcpServers": {
    "azure-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-azure-documentation"]
    }
  }
}
```

For local development without Docker:

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

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_documentation` | Search Azure documentation by keyword query with optional section filtering |
| `read_documentation` | Retrieve the full content of a specific documentation page |

### search_documentation

Search Azure documentation using full-text search with stemming support.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search terms (supports stemming) |
| `section` | string | No | None | Filter by section (Azure service/product directory) |
| `limit` | integer | No | 10 | Maximum results (1-50) |

**Common Sections:** `azure-functions`, `app-service`, `storage`, `virtual-machines`, `aks`, `azure-sql`, `cosmos-db`, `active-directory`, `azure-monitor`

### read_documentation

Retrieve the full content of a documentation page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Relative path to document (from search results) |

## CLI Commands

```bash
# Build/rebuild the documentation index
uv run azure-docs-index index
uv run azure-docs-index index --rebuild
uv run azure-docs-index index --branch main

# Show index statistics
uv run azure-docs-index stats
```

## Development

```bash
make init       # Initialise development environment
make build      # Run full build (lint, typecheck, test)
make test       # Run tests with coverage
make format     # Format code
make lint       # Run linter
make typecheck  # Run type checker
```

## Documentation

- [USAGE.md](USAGE.md) - Detailed usage instructions
- [CODESTYLE.md](CODESTYLE.md) - Code style guidelines
- [CLAUDE.md](CLAUDE.md) - Claude Code instructions

## Licence

This project is licensed under the MIT Licence - see the [LICENSE](LICENSE) file for details.
