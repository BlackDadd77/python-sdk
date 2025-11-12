#!/usr/bin/env ruby
# frozen_string_literal: true

require 'json'
require 'open3'

# MCP Ruby Client Example
# This demonstrates how to interact with an MCP server from Ruby
class MCPClient
  def initialize(command, args = [])
    @command = command
    @args = args
    @message_id = 0
  end

  def connect
    @stdin, @stdout, @stderr, @wait_thr = Open3.popen3(@command, *@args)
    @stdin.sync = true
    initialize_session
  end

  def close
    @stdin.close unless @stdin.closed?
    @stdout.close unless @stdout.closed?
    @stderr.close unless @stderr.closed?
    @wait_thr.join
  end

  def initialize_session
    request = {
      jsonrpc: '2.0',
      id: next_id,
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {
          roots: { listChanged: true },
          sampling: {}
        },
        clientInfo: {
          name: 'ruby-mcp-client',
          version: '0.1.0'
        }
      }
    }

    send_request(request)
    response = read_response

    if response['error']
      raise "Initialization failed: #{response['error']}"
    end

    # Send initialized notification
    notification = {
      jsonrpc: '2.0',
      method: 'notifications/initialized'
    }
    send_notification(notification)

    response['result']
  end

  def list_tools
    request = {
      jsonrpc: '2.0',
      id: next_id,
      method: 'tools/list'
    }

    send_request(request)
    response = read_response

    raise "Failed to list tools: #{response['error']}" if response['error']

    response['result']['tools']
  end

  def call_tool(name, arguments = {})
    request = {
      jsonrpc: '2.0',
      id: next_id,
      method: 'tools/call',
      params: {
        name: name,
        arguments: arguments
      }
    }

    send_request(request)
    response = read_response

    raise "Tool call failed: #{response['error']}" if response['error']

    response['result']
  end

  def list_resources
    request = {
      jsonrpc: '2.0',
      id: next_id,
      method: 'resources/list'
    }

    send_request(request)
    response = read_response

    raise "Failed to list resources: #{response['error']}" if response['error']

    response['result']['resources']
  end

  def read_resource(uri)
    request = {
      jsonrpc: '2.0',
      id: next_id,
      method: 'resources/read',
      params: {
        uri: uri
      }
    }

    send_request(request)
    response = read_response

    raise "Failed to read resource: #{response['error']}" if response['error']

    response['result']
  end

  private

  def next_id
    @message_id += 1
  end

  def send_request(request)
    message = JSON.generate(request)
    @stdin.puts(message)
  end

  def send_notification(notification)
    message = JSON.generate(notification)
    @stdin.puts(message)
  end

  def read_response
    line = @stdout.gets
    return nil unless line

    JSON.parse(line)
  rescue JSON::ParserError => e
    { 'error' => { 'code' => -32700, 'message' => "Parse error: #{e.message}" } }
  end
end

# Example usage
if __FILE__ == $PROGRAM_NAME
  # Connect to an MCP server (assuming you have one running)
  # Example: python -m mcp.server.fastmcp examples/servers/basic_tool.py
  
  client = MCPClient.new('python', ['-m', 'examples.servers.everything'])
  
  begin
    puts "Connecting to MCP server..."
    init_result = client.connect
    puts "Connected! Server info: #{init_result['serverInfo']}"
    puts

    # List available tools
    puts "Available tools:"
    tools = client.list_tools
    tools.each do |tool|
      puts "  - #{tool['name']}: #{tool['description']}"
    end
    puts

    # Call a tool (example - adjust based on your server)
    if tools.any? { |t| t['name'] == 'echo' }
      puts "Calling 'echo' tool..."
      result = client.call_tool('echo', { message: 'Hello from Ruby!' })
      puts "Result: #{result}"
      puts
    end

    # List resources if available
    begin
      puts "Available resources:"
      resources = client.list_resources
      resources.each do |resource|
        puts "  - #{resource['uri']}: #{resource['name']}"
      end
      puts

      # Read a resource if available
      if resources.any?
        first_resource = resources.first
        puts "Reading resource: #{first_resource['uri']}"
        content = client.read_resource(first_resource['uri'])
        puts "Content: #{content}"
      end
    rescue => e
      puts "Resources not available: #{e.message}"
    end

  rescue => e
    puts "Error: #{e.message}"
    puts e.backtrace
  ensure
    client.close
    puts "\nConnection closed."
  end
end
