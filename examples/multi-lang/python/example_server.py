from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any
import json

mcp = FastMCP(
    name="Multi-Language Example Server",
    instructions="This server demonstrates MCP integration across multiple languages"
)

@mcp.tool()
def echo(message: str) -> str:
    """Echo a message back to the caller."""
    return f"Echo: {message}"

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@mcp.resource("config://server-info")
def get_server_info() -> str:
    """Get server information and capabilities"""
    info = {
        "name": "Multi-Language Example Server",
        "version": "1.0.0",
        "protocol": "MCP"
    }
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    mcp.run()
