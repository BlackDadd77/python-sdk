package io.modelcontextprotocol.example

import java.io.*
import java.util.concurrent.TimeUnit

/**
 * MCP Python SDK - Kotlin Integration Example
 * This class demonstrates how to interact with MCP servers from Kotlin/JVM
 */
class McpClient(
    private val serverCommand: String,
    private val serverArgs: List<String> = emptyList()
) {
    private var process: Process? = null
    private var writer: BufferedWriter? = null
    private var reader: BufferedReader? = null
    
    /**
     * Start the MCP server process
     */
    fun startServer() {
        println("Starting MCP server...")
        val command = mutableListOf(serverCommand).apply { addAll(serverArgs) }
        
        val processBuilder = ProcessBuilder(command)
            .redirectErrorStream(true)
        
        process = processBuilder.start()
        
        writer = BufferedWriter(OutputStreamWriter(process!!.outputStream))
        reader = BufferedReader(InputStreamReader(process!!.inputStream))
        
        println("✓ Server started")
    }
    
    /**
     * Send a JSON-RPC request to the MCP server
     */
    fun sendRequest(method: String, params: Map<String, Any> = emptyMap()): String? {
        val request = buildJsonRpcRequest(method, params)
        println("Sending request: $request")
        
        writer?.write(request)
        writer?.newLine()
        writer?.flush()
        
        val response = reader?.readLine()
        println("Received response: $response")
        return response
    }
    
    /**
     * Build a JSON-RPC request
     */
    private fun buildJsonRpcRequest(method: String, params: Map<String, Any>): String {
        val paramsJson = params.entries.joinToString(",") { (k, v) -> 
            "\"$k\":${toJsonValue(v)}"
        }
        
        return """{
            "jsonrpc":"2.0",
            "id":${(1..1000).random()},
            "method":"$method",
            "params":{$paramsJson}
        }"""
    }
    
    private fun toJsonValue(value: Any): String = when (value) {
        is String -> "\"$value\""
        is Number -> value.toString()
        is Boolean -> value.toString()
        is Map<*, *> -> {
            val entries = value.entries.joinToString(",") { (k, v) ->
                "\"$k\":${toJsonValue(v!!)}"
            }
            "{$entries}"
        }
        else -> "\"$value\""
    }
    
    /**
     * Initialize the MCP connection
     */
    fun initializeConnection(): String? {
        return sendRequest("initialize", mapOf(
            "protocolVersion" to "2024-11-05",
            "capabilities" to mapOf(
                "tools" to emptyMap<String, Any>(),
                "resources" to emptyMap<String, Any>(),
                "prompts" to emptyMap<String, Any>()
            ),
            "clientInfo" to mapOf(
                "name" to "kotlin-mcp-client",
                "version" to "1.0.0"
            )
        ))
    }
    
    /**
     * List available tools
     */
    fun listTools(): String? {
        return sendRequest("tools/list")
    }
    
    /**
     * Call a tool
     */
    fun callTool(toolName: String, arguments: Map<String, Any> = emptyMap()): String? {
        return sendRequest("tools/call", mapOf(
            "name" to toolName,
            "arguments" to arguments
        ))
    }
    
    /**
     * List available resources
     */
    fun listResources(): String? {
        return sendRequest("resources/list")
    }
    
    /**
     * Read a resource
     */
    fun readResource(uri: String): String? {
        return sendRequest("resources/read", mapOf("uri" to uri))
    }
    
    /**
     * Stop the server
     */
    fun stopServer() {
        println("Stopping MCP server...")
        writer?.close()
        reader?.close()
        process?.destroy()
        process?.waitFor(5, TimeUnit.SECONDS)
        println("✓ Server stopped")
    }
}

/**
 * Example usage demonstrating MCP integration from Kotlin
 */
object McpExample {
    @JvmStatic
    fun main(args: Array<String>) {
        println("===================================")
        println("MCP Python SDK - Kotlin Integration")
        println("===================================")
        
        val client = McpClient("uv", listOf("run", "python", "-m", "mcp"))
        
        try {
            // Start the server
            client.startServer()
            Thread.sleep(1000) // Give server time to start
            
            // Initialize connection
            println("\nInitializing MCP connection...")
            client.initializeConnection()
            
            // List available tools
            println("\nListing tools...")
            client.listTools()
            
            // Example: Call a tool (if available)
            // val response = client.callTool("example_tool", mapOf("input" to "test"))
            // println("Tool response: $response")
            
            // List resources
            println("\nListing resources...")
            client.listResources()
            
            println("\n✓ Integration example completed successfully!")
            
        } catch (e: Exception) {
            println("Error: ${e.message}")
            e.printStackTrace()
        } finally {
            // Clean up
            client.stopServer()
        }
    }
    
    /**
     * Create an example MCP server file
     */
    fun createExampleServer() {
        val serverCode = """
            """
            Example MCP Server
            Created by Kotlin script
            """
            from mcp.server.fastmcp import FastMCP
            
            mcp = FastMCP("Kotlin Example Server")
            
            @mcp.tool()
            def process_text(text: str, operation: str = "uppercase") -> str:
                '''Process text with various operations'''
                if operation == "uppercase":
                    return text.upper()
                elif operation == "lowercase":
                    return text.lower()
                elif operation == "reverse":
                    return text[::-1]
                else:
                    return text
            
            @mcp.tool()
            def calculate_sum(numbers: list) -> float:
                '''Calculate sum of numbers'''
                return sum(numbers)
            
            @mcp.resource("config://app-settings")
            def get_settings() -> str:
                '''Get application settings'''
                return '{"language": "kotlin", "version": "1.9", "jvm": "17"}'
            
            if __name__ == "__main__":
                mcp.run()
        """.trimIndent()
        
        File("kotlin_example_server.py").writeText(serverCode)
        println("✓ Created example server: kotlin_example_server.py")
    }
}
