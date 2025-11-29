#!/usr/bin/env ruby
# frozen_string_literal: true

# Example: How to use the MCPClient class programmatically
# This demonstrates calling MCP tools from Ruby code

require_relative 'connect_mcp'

def example_echo_tool
  puts "=" * 60
  puts "Example: Calling echo tool programmatically"
  puts "=" * 60
  
  # Create a client connected to a test server
  client = MCPClient.new(
    command: 'python3',
    args: ['/tmp/test_mcp_server.py']
  )
  
  begin
    # Connect to the server
    client.connect
    
    # Call the echo tool
    result = client.call_tool('echo', {
      'message' => 'Hello from programmatic Ruby!'
    })
    
    puts "\nSuccess! Tool returned result."
    
  rescue => e
    puts "Error: #{e.message}"
  ensure
    client.disconnect
  end
end

def example_math_tool
  puts "\n" + "=" * 60
  puts "Example: Calling math tool programmatically"
  puts "=" * 60
  
  client = MCPClient.new(
    command: 'python3',
    args: ['/tmp/test_mcp_server.py']
  )
  
  begin
    client.connect
    
    # Call the add tool with numbers
    result = client.call_tool('add', {
      'a' => 100,
      'b' => 250
    })
    
    puts "\nSuccess! Math calculation completed."
    
  rescue => e
    puts "Error: #{e.message}"
  ensure
    client.disconnect
  end
end

def example_list_and_call
  puts "\n" + "=" * 60
  puts "Example: Discover and call tools dynamically"
  puts "=" * 60
  
  client = MCPClient.new(
    command: 'python3',
    args: ['/tmp/test_mcp_server.py']
  )
  
  begin
    client.connect
    
    # List all available tools
    tools = client.list_tools
    
    # Find and call the first tool
    if tools.any?
      first_tool = tools.first
      puts "\nDynamically calling first available tool: #{first_tool['name']}"
      
      # Call it with appropriate arguments based on the tool
      if first_tool['name'] == 'echo'
        client.call_tool('echo', { 'message' => 'Dynamic call!' })
      end
    end
    
  rescue => e
    puts "Error: #{e.message}"
  ensure
    client.disconnect
  end
end

# Run the examples
if __FILE__ == $PROGRAM_NAME
  puts "MCP Ruby Client - Programmatic Usage Examples"
  puts "=" * 60
  puts ""
  
  # Check if test server is available
  unless File.exist?('/tmp/test_mcp_server.py')
    puts "Error: Test server not found at /tmp/test_mcp_server.py"
    puts "Please create the test server first."
    exit 1
  end
  
  example_echo_tool
  example_math_tool
  example_list_and_call
  
  puts "\n" + "=" * 60
  puts "All examples completed successfully!"
  puts "=" * 60
end
