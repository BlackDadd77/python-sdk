#!/usr/bin/env ruby
# frozen_string_literal: true

require 'json'
require 'open3'

# Ruby client for connecting to Model Context Protocol (MCP) servers
# This demonstrates how to connect to and interact with MCP servers from Ruby
class MCPClient
  PROTOCOL_VERSION = '2025-06-18'

  attr_reader :server_name

  def initialize(command:, args: [], env: {})
    @command = command
    @args = args
    @env = env
    @request_id = 0
    @server_name = nil
    @stdin = nil
    @stdout = nil
    @stderr = nil
    @thread = nil
  end

  # Start the server process and initialize the connection
  def connect
    puts "Starting MCP server: #{@command} #{@args.join(' ')}"

    # Launch the server process
    @stdin, @stdout, @stderr, @thread = Open3.popen3(
      @env,
      @command,
      *@args
    )

    puts "Server process started (PID: #{@thread.pid})"

    # Perform MCP initialization handshake
    initialize_connection
  end

  # Perform the MCP initialization handshake
  def initialize_connection
    puts "\nInitializing MCP connection..."

    request = {
      jsonrpc: '2.0',
      id: next_request_id,
      method: 'initialize',
      params: {
        protocolVersion: PROTOCOL_VERSION,
        capabilities: {
          roots: {
            listChanged: true
          }
        },
        clientInfo: {
          name: 'ruby-mcp-client',
          version: '0.1.0'
        }
      }
    }

    response = send_request(request)

    if response['error']
      raise "Initialization failed: #{response['error']['message']}"
    end

    @server_name = response.dig('result', 'serverInfo', 'name')
    protocol_version = response.dig('result', 'protocolVersion')
    capabilities = response.dig('result', 'capabilities')

    puts "✓ Connected to server: #{@server_name}"
    puts "  Protocol version: #{protocol_version}"
    puts "  Server capabilities: #{capabilities.keys.join(', ')}"

    # Send initialized notification
    send_notification({
      jsonrpc: '2.0',
      method: 'notifications/initialized',
      params: {}
    })

    response['result']
  end

  # List available tools from the server
  def list_tools
    puts "\nListing available tools..."

    request = {
      jsonrpc: '2.0',
      id: next_request_id,
      method: 'tools/list',
      params: {}
    }

    response = send_request(request)

    if response['error']
      raise "Failed to list tools: #{response['error']['message']}"
    end

    tools = response.dig('result', 'tools') || []
    puts "✓ Found #{tools.length} tool(s)"

    tools.each do |tool|
      puts "\n  Tool: #{tool['name']}"
      puts "  Description: #{tool['description']}" if tool['description']
      if tool['inputSchema'] && tool['inputSchema']['properties']
        puts "  Parameters:"
        tool['inputSchema']['properties'].each do |name, prop|
          required = tool['inputSchema']['required']&.include?(name) ? ' (required)' : ''
          puts "    - #{name}: #{prop['description'] || 'No description'}#{required}"
        end
      end
    end

    tools
  end

  # Execute a tool with the given arguments
  def call_tool(tool_name, arguments = {})
    puts "\nCalling tool: #{tool_name}"
    puts "Arguments: #{arguments.to_json}"

    request = {
      jsonrpc: '2.0',
      id: next_request_id,
      method: 'tools/call',
      params: {
        name: tool_name,
        arguments: arguments
      }
    }

    response = send_request(request)

    if response['error']
      raise "Tool execution failed: #{response['error']['message']}"
    end

    result = response['result']
    puts "✓ Tool executed successfully"

    # Display the result
    if result['content']
      result['content'].each do |content_item|
        if content_item['type'] == 'text'
          puts "\nResult:"
          puts content_item['text']
        end
      end
    end

    result
  end

  # List available resources from the server
  def list_resources
    puts "\nListing available resources..."

    request = {
      jsonrpc: '2.0',
      id: next_request_id,
      method: 'resources/list',
      params: {}
    }

    response = send_request(request)

    if response['error']
      # Not all servers support resources, so we don't raise an error
      puts "  (Resources not supported by this server)"
      return []
    end

    resources = response.dig('result', 'resources') || []
    puts "✓ Found #{resources.length} resource(s)"

    resources.each do |resource|
      puts "\n  Resource: #{resource['uri']}"
      puts "  Name: #{resource['name']}" if resource['name']
      puts "  Description: #{resource['description']}" if resource['description']
    end

    resources
  end

  # Close the connection and clean up
  def disconnect
    puts "\nDisconnecting from MCP server..."

    begin
      @stdin.close unless @stdin.closed?
      @stdout.close unless @stdout.closed?
      @stderr.close unless @stderr.closed?

      # Wait for process to exit with timeout
      timeout = 2
      result = @thread.join(timeout)
      unless result
        puts "Server didn't exit gracefully, terminating..."
        Process.kill('TERM', @thread.pid) rescue nil
        @thread.join(1) || Process.kill('KILL', @thread.pid) rescue nil
      end
    rescue => e
      puts "Error during disconnect: #{e.message}"
    end

    puts "✓ Disconnected"
  end

  private

  def next_request_id
    @request_id += 1
  end

  def send_request(request)
    # Write request to stdin
    json_str = request.to_json
    @stdin.puts(json_str)
    @stdin.flush

    # Read response from stdout
    read_response
  end

  def send_notification(notification)
    # Write notification to stdin (no response expected)
    json_str = notification.to_json
    @stdin.puts(json_str)
    @stdin.flush
  end

  def read_response
    # Read a single line from stdout and parse as JSON
    line = @stdout.gets
    raise "Connection closed unexpectedly" if line.nil?

    JSON.parse(line.strip)
  rescue JSON::ParserError => e
    raise "Failed to parse response: #{e.message}\nReceived: #{line}"
  end
end

# Example usage and demonstration
def main
  if ARGV.empty?
    puts "Usage: ruby connect_mcp.rb <command> [args...]"
    puts ""
    puts "Example:"
    puts "  ruby connect_mcp.rb uvx mcp-server-time"
    puts "  ruby connect_mcp.rb npx -y @modelcontextprotocol/server-everything"
    puts ""
    puts "This script demonstrates how to connect to MCP servers from Ruby."
    exit 1
  end

  command = ARGV[0]
  args = ARGV[1..]

  client = MCPClient.new(command: command, args: args)

  begin
    # Connect to the server
    client.connect

    # List available tools
    tools = client.list_tools

    # List available resources (if supported)
    resources = client.list_resources

    # If there are tools, demonstrate calling the first one with sample data
    if tools.any?
      puts "\n" + "=" * 60
      puts "Demonstration complete!"
      puts "=" * 60
      puts "\nYou can now use this client to:"
      puts "  - Initialize connection to MCP servers"
      puts "  - List available tools and resources"
      puts "  - Call tools with arguments"
      puts "  - Handle JSON-RPC communication"
    end
  rescue => e
    puts "\nError: #{e.message}"
    puts e.backtrace.first(5).join("\n")
    exit 1
  ensure
    client.disconnect
  end
end

# Run the main function if this script is executed directly
main if __FILE__ == $PROGRAM_NAME
