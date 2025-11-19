# Ruby MCP Client - connect_mcp.rb

A simple Ruby script that demonstrates how to connect to Model Context Protocol (MCP) servers. This example shows Ruby developers how to integrate with MCP servers using JSON-RPC over stdio transport.

## Overview

The `connect_mcp.rb` script provides a basic but complete implementation of an MCP client in Ruby. It demonstrates:

- Launching and connecting to MCP servers via stdio transport
- Performing the MCP initialization handshake
- Listing available tools and resources
- JSON-RPC 2.0 communication protocol
- Proper cleanup and error handling

## Requirements

- Ruby 3.0 or higher
- An MCP server to connect to

## Usage

### Basic Usage

```bash
ruby connect_mcp.rb <command> [args...]
```

### Examples

**Connect to a Python MCP server:**
```bash
ruby connect_mcp.rb python3 /path/to/mcp_server.py
```

**Connect to an npm-based MCP server:**
```bash
ruby connect_mcp.rb npx -y @modelcontextprotocol/server-everything
```

**Connect to a uvx-based MCP server:**
```bash
ruby connect_mcp.rb uvx mcp-server-time
```

## What It Does

When you run the script, it will:

1. **Start the MCP server** - Launches the specified command as a subprocess
2. **Initialize the connection** - Performs the MCP protocol handshake
3. **List tools** - Queries and displays all available tools from the server
4. **List resources** - Queries and displays all available resources (if supported)
5. **Display results** - Shows the server capabilities and available features
6. **Clean disconnect** - Properly closes the connection and terminates the server

## Example Output

```
Starting MCP server: python3 /tmp/test_mcp_server.py
Server process started (PID: 12345)

Initializing MCP connection...
✓ Connected to server: test-server
  Protocol version: 2025-06-18
  Server capabilities: tools

Listing available tools...
✓ Found 2 tool(s)

  Tool: echo
  Description: Echoes back the provided message
  Parameters:
    - message: The message to echo (required)

  Tool: add
  Description: Adds two numbers together
    - a: First number (required)
    - b: Second number (required)

============================================================
Demonstration complete!
============================================================

You can now use this client to:
  - Initialize connection to MCP servers
  - List available tools and resources
  - Call tools with arguments
  - Handle JSON-RPC communication

Disconnecting from MCP server...
✓ Disconnected
```

## How It Works

### MCP Protocol Implementation

The script implements the core MCP protocol:

1. **JSON-RPC Communication**: All messages use JSON-RPC 2.0 format
2. **Stdio Transport**: Communication happens over stdin/stdout
3. **Initialize Handshake**: 
   - Client sends `initialize` request with protocol version and capabilities
   - Server responds with its protocol version, capabilities, and server info
   - Client sends `notifications/initialized` to complete the handshake

### Code Structure

The `MCPClient` class provides:

- `connect()` - Start the server and initialize the connection
- `initialize_connection()` - Perform the MCP handshake
- `list_tools()` - Query available tools
- `call_tool(name, arguments)` - Execute a tool with arguments
- `list_resources()` - Query available resources
- `disconnect()` - Clean up and close the connection

### Extending the Client

You can easily extend this client to:

**Call a specific tool:**
```ruby
client = MCPClient.new(command: "python3", args: ["/path/to/server.py"])
client.connect

# Call a tool
result = client.call_tool("echo", { "message" => "Hello from Ruby!" })
puts result

client.disconnect
```

**Handle prompts:**
```ruby
def list_prompts
  request = {
    jsonrpc: '2.0',
    id: next_request_id,
    method: 'prompts/list',
    params: {}
  }
  send_request(request)
end
```

**Read resources:**
```ruby
def read_resource(uri)
  request = {
    jsonrpc: '2.0',
    id: next_request_id,
    method: 'resources/read',
    params: { uri: uri }
  }
  send_request(request)
end
```

## MCP Protocol Reference

For more information about the Model Context Protocol:

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [Python SDK Examples](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples)

## Testing

To test the client, you can use the included test server:

```bash
# The test server is created in /tmp during testing
ruby connect_mcp.rb python3 /tmp/test_mcp_server.py
```

Or use any MCP-compatible server from the Python SDK examples:

```bash
cd examples/servers/simple-tool
ruby ../../../connect_mcp.rb python -m mcp_simple_tool
```

## Limitations

This is a demonstration client that:

- Only implements basic MCP features (initialize, tools, resources)
- Uses synchronous I/O (blocking reads/writes)
- Doesn't implement all MCP features (prompts, sampling, etc.)
- Is meant for learning and simple integrations

For production use, consider:

- Implementing async I/O
- Adding robust error handling and retries
- Implementing all MCP protocol features
- Adding logging and debugging capabilities
- Using a proper Ruby gem structure

## License

This example is provided as part of the MCP Python SDK and follows the same license (MIT).
