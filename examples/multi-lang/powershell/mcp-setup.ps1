# MCP Python SDK - PowerShell Integration Example
# This script demonstrates how to interact with MCP servers from PowerShell

# Function to check if Python is installed
function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
        return $false
    }
}

# Function to check if uv is installed
function Test-UvInstallation {
    try {
        $uvVersion = uv --version 2>&1
        Write-Host "✓ uv installed: $uvVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ uv not found. Installing uv..." -ForegroundColor Yellow
        pip install uv
        return $true
    }
}

# Function to install MCP SDK
function Install-McpSdk {
    Write-Host "`nInstalling MCP Python SDK..." -ForegroundColor Cyan
    uv add "mcp[cli]"
    Write-Host "✓ MCP SDK installed successfully" -ForegroundColor Green
}

# Function to run MCP server
function Start-McpServer {
    param(
        [string]$ServerScript = "server.py"
    )
    
    Write-Host "`nStarting MCP server: $ServerScript" -ForegroundColor Cyan
    
    if (Test-Path $ServerScript) {
        uv run python $ServerScript
    }
    else {
        Write-Host "✗ Server script not found: $ServerScript" -ForegroundColor Red
    }
}

# Function to test MCP server with inspector
function Test-McpServer {
    param(
        [string]$ServerScript = "server.py"
    )
    
    Write-Host "`nTesting MCP server with inspector..." -ForegroundColor Cyan
    uv run mcp dev $ServerScript
}

# Function to install MCP server in Claude Desktop
function Install-McpInClaude {
    param(
        [string]$ServerScript = "server.py",
        [string]$ServerName = "example-server"
    )
    
    Write-Host "`nInstalling MCP server in Claude Desktop..." -ForegroundColor Cyan
    uv run mcp install $ServerScript --name $ServerName
    Write-Host "✓ Server installed successfully" -ForegroundColor Green
}

# Function to create example MCP server
function New-ExampleMcpServer {
    param(
        [string]$FileName = "example-server.py"
    )
    
    $serverContent = @'
"""
Example MCP Server
Created by PowerShell script
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Example Server")

@mcp.tool()
def greet(name: str = "World") -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"

@mcp.tool()
def calculate(operation: str, a: float, b: float) -> float:
    """Perform basic arithmetic"""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else float('inf')
    }
    return operations.get(operation, 0.0)

@mcp.resource("config://settings")
def get_settings() -> str:
    """Get server settings"""
    return '{"debug": false, "version": "1.0.0"}'

if __name__ == "__main__":
    mcp.run()
'@
    
    Set-Content -Path $FileName -Value $serverContent
    Write-Host "✓ Created example server: $FileName" -ForegroundColor Green
}

# Main execution
function Main {
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "MCP Python SDK - PowerShell Setup" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    
    # Check prerequisites
    if (-not (Test-PythonInstallation)) {
        exit 1
    }
    
    Test-UvInstallation
    
    # Display menu
    Write-Host "`nAvailable commands:" -ForegroundColor Yellow
    Write-Host "1. Create example server"
    Write-Host "2. Install MCP SDK"
    Write-Host "3. Test server with inspector"
    Write-Host "4. Install server in Claude Desktop"
    Write-Host ""
    
    Write-Host "Usage examples:" -ForegroundColor Green
    Write-Host "  New-ExampleMcpServer -FileName 'my-server.py'"
    Write-Host "  Test-McpServer -ServerScript 'my-server.py'"
    Write-Host "  Install-McpInClaude -ServerScript 'my-server.py' -ServerName 'MyServer'"
}

# Run main function
Main

# Export functions for use in PowerShell session
Export-ModuleMember -Function @(
    'Test-PythonInstallation',
    'Test-UvInstallation',
    'Install-McpSdk',
    'Start-McpServer',
    'Test-McpServer',
    'Install-McpInClaude',
    'New-ExampleMcpServer'
)
