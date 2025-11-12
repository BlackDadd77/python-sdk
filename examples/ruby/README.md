# MCP Ruby Client Example

This directory contains a Ruby implementation of an MCP (Model Context Protocol) client that demonstrates how to interact with Python MCP servers from Ruby applications.

## Features

- JSON-RPC 2.0 communication over stdio
- Initialize MCP sessions
- List and call tools
- List and read resources
- Error handling and connection management

## Prerequisites

- Ruby >= 2.7.0
- Bundler
- A running MCP server (Python)

## Installation

```bash
# Install dependencies
bundle install
```

## Usage

### Basic Usage

```bash
# Make the script executable
chmod +x mcp_client.rb

# Run the client (connects to example server)
./mcp_client.rb
```

### Using with Your Own Server

Edit the `mcp_client.rb` file and modify the connection parameters:

```ruby
# Connect to your MCP server
client = MCPClient.new('python', ['-m', 'your.server.module'])
```

### Programmatic Usage

```ruby
require_relative 'mcp_client'

client = MCPClient.new('python', ['-m', 'examples.servers.everything'])

begin
  # Initialize connection
  client.connect
  
  # List available tools
  tools = client.list_tools
  tools.each do |tool|
    puts "Tool: #{tool['name']}"
  end
  
  # Call a tool
  result = client.call_tool('echo', { message: 'Hello!' })
  puts "Result: #{result}"
  
ensure
  client.close
end
```

## API Reference

### MCPClient

#### Methods

- `initialize(command, args = [])` - Create a new client instance
- `connect` - Connect to the MCP server and initialize the session
- `close` - Close the connection to the server
- `list_tools` - Get list of available tools from the server
- `call_tool(name, arguments = {})` - Call a specific tool with arguments
- `list_resources` - Get list of available resources
- `read_resource(uri)` - Read content of a specific resource

## Example Output

```
Connecting to MCP server...
Connected! Server info: {"name"=>"example-server", "version"=>"0.1.0"}

Available tools:
  - echo: Echo back the provided message
  - calculate: Perform basic calculations

Calling 'echo' tool...
Result: {"content"=>[{"type"=>"text", "text"=>"Hello from Ruby!"}]}

Connection closed.
```

## Error Handling

The client includes error handling for:
- Connection failures
- Protocol errors
- Tool execution errors
- Resource access errors

## Contributing

Feel free to submit issues and enhancement requests!

## License

This example is part of the MCP Python SDK and follows the same license.
