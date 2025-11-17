# Multi-Language Integration Examples

This directory contains comprehensive examples demonstrating how to integrate the MCP Python SDK with various programming languages and technologies.

## 📁 Directory Structure

```
multi-lang/
├── json/               # JSON configuration examples
├── html/               # HTML documentation templates
├── powershell/         # PowerShell integration scripts
├── kotlin/             # Kotlin/JVM integration
├── docker/             # Docker containerization
├── ruby/               # Ruby integration examples
└── python/             # Python examples (reference)
```

## 🚀 Quick Start

### JSON Configuration

The `json/` directory contains example configuration files for MCP servers and clients:

- `server-config.json` - MCP server configuration template
- `client-config.json` - MCP client configuration template

```bash
# Validate JSON configuration
python -m json.tool examples/multi-lang/json/server-config.json
```

### HTML Documentation

The `html/` directory contains example HTML documentation:

```bash
# View the documentation
open examples/multi-lang/html/example-docs.html
```

### PowerShell Integration

The `powershell/` directory contains scripts for Windows environments:

```powershell
# Import the MCP PowerShell module
. .\examples\multi-lang\powershell\mcp-setup.ps1

# Create an example server
New-ExampleMcpServer -FileName "my-server.py"

# Test the server
Test-McpServer -ServerScript "my-server.py"

# Install in Claude Desktop
Install-McpInClaude -ServerScript "my-server.py" -ServerName "MyServer"
```

### Kotlin/JVM Integration

The `kotlin/` directory shows how to interact with MCP from Kotlin:

```bash
# Compile and run the Kotlin example
cd examples/multi-lang/kotlin
kotlinc McpClient.kt -include-runtime -d mcp-client.jar
java -jar mcp-client.jar
```

Or using Gradle:

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
}
```

### Docker Containerization

The `docker/` directory contains Dockerfiles and compose files:

```bash
# Build the Docker image
cd examples/multi-lang/docker
docker build -t mcp-python-sdk:latest -f Dockerfile ../../..

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f mcp-server-http

# Stop services
docker-compose down
```

### Ruby Integration

The `ruby/` directory contains Ruby scripts for MCP integration:

```bash
# Run the Ruby example
cd examples/multi-lang/ruby
ruby mcp_client.rb

# Or use it as a library
irb -r ./mcp_client.rb
```

## 🔧 Integration Patterns

### Pattern 1: Command-Line Integration

All languages can interact with MCP servers via command-line execution:

**Python:**
```python
import subprocess
result = subprocess.run(["uv", "run", "mcp", "dev", "server.py"], capture_output=True)
```

**Ruby:**
```ruby
Open3.popen3("uv", "run", "mcp", "dev", "server.py")
```

**Kotlin:**
```kotlin
ProcessBuilder("uv", "run", "mcp", "dev", "server.py").start()
```

**PowerShell:**
```powershell
Start-Process "uv" -ArgumentList "run","mcp","dev","server.py"
```

### Pattern 2: JSON-RPC Communication

MCP uses JSON-RPC 2.0 for communication over stdio:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

All languages can send/receive JSON messages through stdin/stdout.

### Pattern 3: HTTP Transport

For HTTP-based integration (Streamable HTTP or SSE):

**cURL:**
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
```

**Kotlin:**
```kotlin
val client = HttpClient()
client.post("http://localhost:8000/mcp") {
    contentType(ContentType.Application.Json)
    setBody("""{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}""")
}
```

## 📚 Example Use Cases

### Use Case 1: Cross-Platform Development

Use PowerShell on Windows and Bash on Unix-like systems to manage MCP servers:

```powershell
# Windows
.\examples\multi-lang\powershell\mcp-setup.ps1
```

```bash
# Unix/Linux/macOS
./examples/multi-lang/shell/mcp-setup.sh
```

### Use Case 2: Containerized Deployment

Deploy MCP servers in containers for cloud environments:

```bash
# Build and deploy
docker build -t mcp-server .
docker run -p 8000:8000 mcp-server

# Or with Kubernetes
kubectl apply -f mcp-deployment.yaml
```

### Use Case 3: Polyglot Applications

Integrate MCP into applications written in different languages:

- **Backend (Python)**: MCP server providing tools and resources
- **Frontend (JavaScript/TypeScript)**: Web client consuming MCP
- **Mobile (Kotlin)**: Android app using MCP for AI features
- **Scripts (Ruby/PowerShell)**: Automation and deployment

## 🧪 Testing

### Validate All Examples

Run the multi-language workflow:

```bash
# Trigger the workflow
gh workflow run multi-language-examples.yml

# Or test locally
.github/workflows/test-multi-lang.sh
```

### Individual Tests

Test each integration separately:

```bash
# JSON validation
python -m json.tool examples/multi-lang/json/*.json

# HTML validation
tidy -q -e examples/multi-lang/html/*.html

# PowerShell syntax check
pwsh -Command "Test-Path examples/multi-lang/powershell/*.ps1"

# Kotlin compilation
kotlinc examples/multi-lang/kotlin/*.kt

# Ruby syntax check
ruby -c examples/multi-lang/ruby/*.rb

# Docker build
docker build -f examples/multi-lang/docker/Dockerfile .
```

## 🤝 Contributing

When adding new language examples:

1. Create a new directory under `multi-lang/`
2. Add example code with clear comments
3. Update this README with usage instructions
4. Add tests to the GitHub Actions workflow
5. Ensure examples follow the repository's development guidelines

## 📖 Additional Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- [MCP Python SDK Documentation](https://modelcontextprotocol.github.io/python-sdk/)
- [GitHub Actions Workflow Reference](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)

## 🐛 Troubleshooting

### Common Issues

**Issue**: PowerShell execution policy prevents running scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: Docker build fails with permission errors
```bash
# Run with sudo or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Issue**: Kotlin compilation errors
```bash
# Ensure Kotlin is installed
sdk install kotlin
# Or with SDKMAN
curl -s "https://get.sdkman.io" | bash
```

**Issue**: Ruby gem dependencies
```bash
# Install bundler and dependencies
gem install bundler
bundle install
```

## 📝 License

These examples are part of the MCP Python SDK and are licensed under the MIT License.
