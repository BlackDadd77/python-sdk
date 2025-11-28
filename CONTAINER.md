# MCP Multi-Language Development Container

This directory contains Docker configuration for a multi-language development environment supporting Python, Ruby, and Node.js for MCP development.

## Features

- **Python 3.11** with uv package manager
- **Ruby** with Bundler
- **Node.js** with npm and TypeScript
- Pre-configured development environment
- Multiple service configurations via docker-compose

## Quick Start

### Using Docker

```bash
# Build the container
docker build -t mcp-sdk .

# Run interactive shell
docker run -it -v $(pwd):/workspace mcp-sdk

# Run a specific command
docker run --rm -v $(pwd):/workspace mcp-sdk uv run python -m examples.servers.basic_tool
```

### Using Docker Compose

```bash
# Start development container
docker-compose run --rm mcp-dev

# Start MCP server
docker-compose up mcp-server

# Start HTTP streaming server
docker-compose up mcp-http-server

# Start documentation server
docker-compose up docs-server

# Build all services
docker-compose build

# Stop all services
docker-compose down
```

## Available Services

### mcp-dev
Interactive development environment with all languages installed.

```bash
docker-compose run --rm mcp-dev
```

### mcp-server
Runs a stdio-based MCP server example.

```bash
docker-compose up mcp-server
```

### mcp-http-server
Runs an HTTP streaming MCP server on port 8000.

```bash
docker-compose up mcp-http-server
# Access at http://localhost:8000
```

### docs-server
Serves the MkDocs documentation on port 8080.

```bash
docker-compose up docs-server
# Access at http://localhost:8080
```

## Development Workflow

### Python Development

```bash
# Enter development container
docker-compose run --rm mcp-dev

# Inside container:
uv run pytest                    # Run tests
uv run ruff check .              # Lint code
uv run pyright                   # Type check
uv run python -m examples.servers.basic_tool  # Run example
```

### Ruby Development

```bash
# Enter development container
docker-compose run --rm mcp-dev

# Inside container:
cd examples/ruby
bundle install                   # Install dependencies
ruby mcp_client.rb               # Run Ruby client
```

### Multi-Language Testing

```bash
# Test all languages
docker-compose run --rm mcp-dev bash -c "
  python --version &&
  ruby --version &&
  node --version
"
```

## Customization

### Adding Dependencies

**Python:**
Edit `pyproject.toml` and rebuild:
```bash
docker-compose build mcp-dev
```

**Ruby:**
Edit `examples/ruby/Gemfile` and rebuild:
```bash
docker-compose build mcp-dev
```

**Node.js:**
Edit `Dockerfile` to add global npm packages:
```dockerfile
RUN npm install -g <package-name>
```

### Environment Variables

Add environment variables in `docker-compose.yml`:

```yaml
services:
  mcp-dev:
    environment:
      - MY_VARIABLE=value
```

## Volumes

- `.:/workspace` - Mounts your local directory
- `mcp-cache:/root/.cache` - Caches package downloads
- `docs-site:/workspace/site` - Stores built documentation

## Ports

- `8000` - HTTP streaming server
- `8080` - Documentation server
- `3000` - Reserved for Node.js apps
- `4000` - Reserved for additional services

## Troubleshooting

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# Run with your user ID
docker-compose run --rm -u $(id -u):$(id -g) mcp-dev
```

### Cache Issues

Clear Docker cache:

```bash
docker-compose down -v
docker system prune -a
```

### Build Issues

Rebuild without cache:

```bash
docker-compose build --no-cache
```

## CI/CD Integration

The container is tested in GitHub Actions. See `.github/workflows/container.yml` for the CI configuration.

## Best Practices

1. **Keep the container updated**: Regularly rebuild to get security updates
2. **Use volumes**: Mount your code directory for hot-reloading
3. **Separate concerns**: Use different services for different tasks
4. **Clean up**: Remove stopped containers and unused images regularly

## Examples

### Running Tests in Container

```bash
# Run all tests
docker-compose run --rm mcp-dev uv run pytest

# Run specific test
docker-compose run --rm mcp-dev uv run pytest tests/test_specific.py
```

### Building and Testing Ruby Client

```bash
docker-compose run --rm mcp-dev bash -c "
  cd examples/ruby &&
  bundle install &&
  ruby mcp_client.rb
"
```

### Interactive Development

```bash
# Start container with shell
docker-compose run --rm mcp-dev bash

# Inside container, you can:
# - Edit files (mounted from host)
# - Run commands
# - Test across languages
# - Exit without losing changes
```

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Visit [modelcontextprotocol.io](https://modelcontextprotocol.io)
- Open an issue on GitHub
