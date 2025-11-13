# MCP Technology Models API Server 🔥

A comprehensive MCP server demonstrating all technology models with secure OAuth authentication.

## Overview

This server showcases the complete Model Context Protocol (MCP) feature set:

- **🔧 Tools**: Execute operations, calculations, and system queries
- **📦 Resources**: Access server data, documentation, and templates
- **💡 Prompts**: Generate contextual prompts for AI interactions
- **✨ Completions**: Intelligent suggestions and auto-completion
- **🔐 Authentication**: Secure OAuth 2.0 authentication with client registration

## Features

### Complete Technology Model Coverage

1. **Tools API**
   - System information retrieval
   - Mathematical calculations
   - Multi-content type responses (text, image, audio)
   - Progress tracking for long-running operations

2. **Resources API**
   - Static resources (status, documentation)
   - Template resources with dynamic parameters
   - Binary resources (images, files)

3. **Prompts API**
   - System analysis prompts
   - Data query prompts with parameters
   - Multimodal prompts (text + images)

4. **Completions API**
   - Context-aware suggestions
   - Argument-based completions
   - Smart filtering

### Secure Authentication

- OAuth 2.0 authorization flow
- Client registration support
- Token management (access + refresh tokens)
- Scope-based access control
- Beautiful login UI

## Installation

```bash
# Install from the examples/servers/tech-models-api directory
uv sync

# Or install in development mode from the root of the repository
uv pip install -e examples/servers/tech-models-api
```

## Usage

### Starting the Server

```bash
# Run with default settings (localhost:8000)
uv run mcp-tech-models-api

# Run on a different port
uv run mcp-tech-models-api --port 3000

# Run on a different host
uv run mcp-tech-models-api --host 0.0.0.0 --port 8080

# Use SSE transport instead of streamable HTTP
uv run mcp-tech-models-api --transport sse
```

### Demo Credentials

For testing purposes, use these credentials:
- **Username**: `demo`
- **Password**: `demo123`

### API Endpoints

Once running, the server provides:

- **MCP Endpoint**: `http://localhost:8000/mcp`
- **OAuth Metadata**: `http://localhost:8000/.well-known/oauth-authorization-server`
- **Login Page**: `http://localhost:8000/login?state=<state>`

## Architecture

### Authentication Flow

1. Client registers via `/register` endpoint
2. Client initiates OAuth flow via `/authorize`
3. User logs in through web interface
4. Authorization code exchanged for tokens at `/token`
5. Access token used for authenticated MCP requests

### API Structure

The server implements the full MCP protocol with:

```
├── Tools (Actions/Operations)
│   ├── get_system_info - Server capabilities
│   ├── calculate - Mathematical operations
│   ├── get_content_types_demo - Multi-content response
│   └── tool_with_progress - Progress tracking
│
├── Resources (Data Access)
│   ├── tech://api/status - Server health
│   ├── tech://api/documentation - API docs
│   ├── tech://data/template/{id} - Dynamic templates
│   └── tech://binary/image - Binary content
│
├── Prompts (AI Interaction)
│   ├── system_analysis_prompt - System analysis
│   ├── data_query_prompt - Data querying
│   └── multimodal_analysis_prompt - Image analysis
│
└── Completions (Auto-suggestions)
    └── Smart context-aware completions
```

## Development

### Running Tests

```bash
# Run tests for this server
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v
```

### Code Quality

```bash
# Run linter
uv run ruff check .

# Run type checker
uv run pyright .
```

## Integration with MCP Clients

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "tech-models-api": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/python-sdk/examples/servers/tech-models-api",
        "mcp-tech-models-api"
      ],
      "transport": "streamable-http",
      "env": {
        "FASTMCP_PORT": "8000"
      }
    }
  }
}
```

### Python Client

```python
from mcp.client import Client
from mcp.client.streamable_http import StreamableHTTPTransport

async def connect():
    transport = StreamableHTTPTransport("http://localhost:8000/mcp")
    
    async with Client(transport) as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        # Call a tool
        result = await client.call_tool("get_system_info", {})
        print(f"System info: {result}")
```

## Security Considerations

⚠️ **Important**: This server is designed for demonstration and development purposes.

For production use:
- Replace in-memory storage with persistent databases
- Use proper secret management (not hardcoded credentials)
- Implement rate limiting
- Add request validation and sanitization
- Use HTTPS in production
- Implement proper session management
- Add comprehensive logging and monitoring

## License

MIT License - See the root LICENSE file for details.

## Contributing

Contributions are welcome! Please see the main repository's CONTRIBUTING.md for guidelines.
