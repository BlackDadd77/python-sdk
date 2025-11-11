#!/usr/bin/env ruby
# MCP Python SDK - Ruby Integration Example
# This script demonstrates how to interact with MCP servers from Ruby

require 'json'
require 'open3'

class McpClient
  attr_reader :server_process
  
  def initialize(server_command, server_args = [])
    @server_command = server_command
    @server_args = server_args
    @server_process = nil
  end
  
  # Start the MCP server process
  def start_server
    puts "Starting MCP server..."
    @stdin, @stdout, @stderr, @wait_thr = Open3.popen3(@server_command, *@server_args)
    puts "✓ Server started with PID: #{@wait_thr.pid}"
  end
  
  # Send a request to the MCP server
  def send_request(method, params = {})
    request = {
      jsonrpc: "2.0",
      id: rand(1..1000),
      method: method,
      params: params
    }
    
    request_json = request.to_json
    puts "Sending request: #{request_json}"
    
    @stdin.puts(request_json)
    @stdin.flush
    
    # Read response
    response_line = @stdout.gets
    return nil if response_line.nil?
    
    response = JSON.parse(response_line)
    puts "Received response: #{response}"
    response
  end
  
  # Initialize the MCP connection
  def initialize_connection
    send_request("initialize", {
      protocolVersion: "2024-11-05",
      capabilities: {
        tools: {},
        resources: {},
        prompts: {}
      },
      clientInfo: {
        name: "ruby-mcp-client",
        version: "1.0.0"
      }
    })
  end
  
  # List available tools
  def list_tools
    response = send_request("tools/list")
    if response && response["result"]
      puts "\nAvailable tools:"
      response["result"]["tools"].each do |tool|
        puts "  - #{tool['name']}: #{tool['description']}"
      end
    end
    response
  end
  
  # Call a tool
  def call_tool(tool_name, arguments = {})
    send_request("tools/call", {
      name: tool_name,
      arguments: arguments
    })
  end
  
  # List available resources
  def list_resources
    response = send_request("resources/list")
    if response && response["result"]
      puts "\nAvailable resources:"
      response["result"]["resources"].each do |resource|
        puts "  - #{resource['uri']}: #{resource['name']}"
      end
    end
    response
  end
  
  # Read a resource
  def read_resource(uri)
    send_request("resources/read", { uri: uri })
  end
  
  # Stop the server
  def stop_server
    if @server_process
      puts "Stopping MCP server..."
      Process.kill('TERM', @wait_thr.pid)
      @stdin.close
      @stdout.close
      @stderr.close
      puts "✓ Server stopped"
    end
  end
end

# Example usage
class McpExample
  def self.run
    puts "==================================="
    puts "MCP Python SDK - Ruby Integration"
    puts "==================================="
    
    # Create client for an MCP server
    client = McpClient.new("uv", ["run", "python", "-m", "mcp"])
    
    begin
      # Start the server
      client.start_server
      sleep 1 # Give server time to start
      
      # Initialize connection
      puts "\nInitializing MCP connection..."
      client.initialize_connection
      
      # List available tools
      client.list_tools
      
      # Example: Call a tool (if available)
      # response = client.call_tool("example_tool", { input: "test" })
      # puts "Tool response: #{response}"
      
      # List resources
      client.list_resources
      
      puts "\n✓ Integration example completed successfully!"
      
    rescue => e
      puts "Error: #{e.message}"
      puts e.backtrace
    ensure
      # Clean up
      client.stop_server
    end
  end
  
  def self.create_example_server
    server_code = <<~PYTHON
      """
      Example MCP Server
      Created by Ruby script
      """
      from mcp.server.fastmcp import FastMCP
      
      mcp = FastMCP("Ruby Example Server")
      
      @mcp.tool()
      def echo(message: str) -> str:
          """Echo a message back"""
          return f"Echo: {message}"
      
      @mcp.tool()
      def process_data(data: dict) -> dict:
          """Process JSON data"""
          return {"processed": True, "input": data}
      
      if __name__ == "__main__":
          mcp.run()
    PYTHON
    
    File.write("ruby_example_server.py", server_code)
    puts "✓ Created example server: ruby_example_server.py"
  end
end

# Run the example if this file is executed directly
if __FILE__ == $0
  McpExample.run
end
