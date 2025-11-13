#!/usr/bin/env python3
"""
MCP Technology Models API Server
A comprehensive API server demonstrating all MCP technology models with secure OAuth authentication.

This server showcases:
- Complete technology model coverage (tools, resources, prompts, completions)
- Secure OAuth authentication
- Streamable HTTP API routes
- Proper error handling and logging
"""

import asyncio
import base64
import json
import logging
import time
from typing import Any

import click
from pydantic import AnyHttpUrl, BaseModel
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from mcp.server.auth.provider import OAuthAuthorizationServerProvider
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage
from mcp.server.session import ServerSession
from mcp.types import (
    AudioContent,
    Completion,
    CompletionArgument,
    CompletionContext,
    ImageContent,
    PromptReference,
    ResourceTemplateReference,
    TextContent,
)

logger = logging.getLogger(__name__)

# Test data for content types
TEST_IMAGE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
TEST_AUDIO_BASE64 = "UklGRiYAAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQIAAAA="


class TechModelAuthSettings(BaseModel):
    """Authentication settings for the tech models API."""

    mcp_scope: str = "mcp"
    demo_username: str = "demo"
    demo_password: str = "demo123"


class TechModelOAuthProvider(OAuthAuthorizationServerProvider[Any, Any, Any]):
    """OAuth provider for the tech models API server."""

    def __init__(self, auth_settings: TechModelAuthSettings, auth_callback_path: str, server_url: str):
        self.auth_settings = auth_settings
        self.auth_callback_path = auth_callback_path
        self.server_url = server_url
        # In-memory storage for demo purposes
        self._clients: dict[str, dict[str, Any]] = {}
        self._auth_codes: dict[str, dict[str, Any]] = {}
        self._access_tokens: dict[str, dict[str, Any]] = {}
        self._refresh_tokens: dict[str, dict[str, Any]] = {}

    async def get_login_page(self, state: str) -> Response:
        """Return a simple HTML login form."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tech Models API - Login</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .login-container {{
                    background: white;
                    padding: 2rem;
                    border-radius: 10px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                    width: 300px;
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                    margin-bottom: 1.5rem;
                }}
                input {{
                    width: 100%;
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    box-sizing: border-box;
                }}
                button {{
                    width: 100%;
                    padding: 10px;
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                button:hover {{
                    background: #5568d3;
                }}
                .info {{
                    margin-top: 1rem;
                    padding: 0.5rem;
                    background: #f0f0f0;
                    border-radius: 5px;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>🔥 Tech Models API</h1>
                <form method="POST" action="{self.auth_callback_path}">
                    <input type="hidden" name="state" value="{state}">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <div class="info">
                    <strong>Demo Credentials:</strong><br>
                    Username: {self.auth_settings.demo_username}<br>
                    Password: {self.auth_settings.demo_password}
                </div>
            </div>
        </body>
        </html>
        """
        return Response(content=html, media_type="text/html")

    async def handle_login_callback(self, request: Request) -> Response:
        """Handle the login form submission."""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        state = form.get("state")

        if not state:
            raise HTTPException(400, "Missing state parameter")

        # Simple credential validation
        if username == self.auth_settings.demo_username and password == self.auth_settings.demo_password:
            # Authentication successful - redirect with success
            # In a real implementation, this would generate an auth code and redirect

            # For demo, we'll just show success
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login Successful</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .success-container {
                        background: white;
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                        text-align: center;
                    }
                    h1 { color: #22c55e; }
                </style>
            </head>
            <body>
                <div class="success-container">
                    <h1>✅ Login Successful!</h1>
                    <p>You have been authenticated. You can now close this window.</p>
                </div>
            </body>
            </html>
            """
            return Response(content=html, media_type="text/html")
        else:
            # Authentication failed
            raise HTTPException(401, "Invalid credentials")

    async def create_client(
        self,
        client_name: str,
        redirect_uris: list[AnyHttpUrl],
        scopes: list[str],
        **kwargs: Any,
    ) -> tuple[str, str]:
        """Create a new OAuth client."""
        client_id = f"client_{int(time.time() * 1000)}"
        client_secret = base64.b64encode(f"{client_id}:secret".encode()).decode()
        
        self._clients[client_id] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": client_name,
            "redirect_uris": [str(uri) for uri in redirect_uris],
            "scopes": scopes,
            "created_at": time.time(),
        }
        
        return client_id, client_secret

    async def get_client(self, client_id: str) -> dict[str, Any] | None:
        """Retrieve client information."""
        return self._clients.get(client_id)

    async def validate_client_secret(self, client_id: str, client_secret: str) -> bool:
        """Validate client credentials."""
        client = self._clients.get(client_id)
        if not client:
            return False
        return client["client_secret"] == client_secret

    async def create_authorization_code(
        self,
        client_id: str,
        redirect_uri: str,
        scopes: list[str],
        code_challenge: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Create an authorization code."""
        auth_code = base64.b64encode(f"code_{int(time.time() * 1000)}".encode()).decode()
        
        self._auth_codes[auth_code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scopes": scopes,
            "code_challenge": code_challenge,
            "created_at": time.time(),
            "expires_at": time.time() + 600,  # 10 minutes
        }
        
        return auth_code

    async def validate_authorization_code(
        self,
        client_id: str,
        code: str,
        redirect_uri: str,
        code_verifier: str | None = None,
    ) -> dict[str, Any] | None:
        """Validate and consume an authorization code."""
        auth_code_data = self._auth_codes.get(code)
        
        if not auth_code_data:
            return None
            
        if auth_code_data["client_id"] != client_id:
            return None
            
        if auth_code_data["redirect_uri"] != redirect_uri:
            return None
            
        if auth_code_data["expires_at"] < time.time():
            return None
        
        # Remove the code after use (one-time use)
        del self._auth_codes[code]
        
        return auth_code_data

    async def create_access_token(
        self,
        client_id: str,
        scopes: list[str],
        resource: str | None = None,
        **kwargs: Any,
    ) -> tuple[str, int]:
        """Create an access token."""
        access_token = base64.b64encode(f"access_{int(time.time() * 1000)}".encode()).decode()
        expires_in = 3600  # 1 hour
        
        self._access_tokens[access_token] = {
            "client_id": client_id,
            "scopes": scopes,
            "resource": resource,
            "created_at": time.time(),
            "expires_at": time.time() + expires_in,
        }
        
        return access_token, expires_in

    async def create_refresh_token(
        self,
        client_id: str,
        scopes: list[str],
        **kwargs: Any,
    ) -> str:
        """Create a refresh token."""
        refresh_token = base64.b64encode(f"refresh_{int(time.time() * 1000)}".encode()).decode()
        
        self._refresh_tokens[refresh_token] = {
            "client_id": client_id,
            "scopes": scopes,
            "created_at": time.time(),
        }
        
        return refresh_token

    async def load_access_token(self, token: str) -> Any:
        """Load access token data."""
        token_data = self._access_tokens.get(token)
        if not token_data:
            return None
            
        if token_data["expires_at"] < time.time():
            return None
            
        # Return a simple object with required attributes
        class TokenData:
            def __init__(self, data: dict[str, Any]):
                self.client_id = data["client_id"]
                self.scopes = data["scopes"]
                self.resource = data.get("resource")
                self.expires_at = data["expires_at"]
        
        return TokenData(token_data)

    async def revoke_token(self, token: str) -> bool:
        """Revoke a token."""
        if token in self._access_tokens:
            del self._access_tokens[token]
            return True
        if token in self._refresh_tokens:
            del self._refresh_tokens[token]
            return True
        return False


def create_tech_models_api_server(
    host: str,
    port: int,
    auth_settings: TechModelAuthSettings,
) -> FastMCP:
    """Create the comprehensive tech models API server with authentication."""
    server_url = AnyHttpUrl(f"http://{host}:{port}")
    
    oauth_provider = TechModelOAuthProvider(
        auth_settings,
        f"http://{host}:{port}/login/callback",
        str(server_url),
    )

    mcp_auth_settings = AuthSettings(
        issuer_url=server_url,
        client_registration_options=ClientRegistrationOptions(
            enabled=True,
            valid_scopes=[auth_settings.mcp_scope],
            default_scopes=[auth_settings.mcp_scope],
        ),
        required_scopes=[auth_settings.mcp_scope],
        resource_server_url=None,
    )

    mcp = FastMCP(
        name="MCP Technology Models API",
        instructions="A comprehensive API server showcasing all MCP technology models with secure authentication",
        auth_server_provider=oauth_provider,
        host=host,
        port=port,
        debug=True,
        auth=mcp_auth_settings,
    )

    # Add custom routes for login
    @mcp.custom_route("/login", methods=["GET"])
    async def login_page_handler(request: Request) -> Response:
        """Show login form."""
        state = request.query_params.get("state")
        if not state:
            raise HTTPException(400, "Missing state parameter")
        return await oauth_provider.get_login_page(state)

    @mcp.custom_route("/login/callback", methods=["POST"])
    async def login_callback_handler(request: Request) -> Response:
        """Handle authentication callback."""
        return await oauth_provider.handle_login_callback(request)

    # ========== TOOLS ==========
    @mcp.tool()
    def get_system_info() -> dict[str, Any]:
        """
        Get system information including server status and capabilities.
        
        Returns comprehensive information about the server's current state,
        supported features, and available resources.
        """
        return {
            "server_name": "MCP Technology Models API",
            "version": "1.0.0",
            "status": "operational",
            "uptime_seconds": time.time(),
            "features": [
                "OAuth Authentication",
                "Tools API",
                "Resources API",
                "Prompts API",
                "Completions API",
            ],
            "supported_content_types": ["text", "image", "audio", "embedded_resource"],
        }

    @mcp.tool()
    def calculate(operation: str, a: float, b: float) -> dict[str, Any]:
        """
        Perform mathematical calculations.
        
        Args:
            operation: The operation to perform (add, subtract, multiply, divide)
            a: First operand
            b: Second operand
        
        Returns:
            Result of the calculation with metadata
        """
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else None,
        }
        
        if operation not in operations:
            return {
                "error": f"Unknown operation: {operation}",
                "supported_operations": list(operations.keys()),
            }
        
        result = operations[operation](a, b)
        
        if result is None:
            return {"error": "Division by zero"}
        
        return {
            "operation": operation,
            "operands": {"a": a, "b": b},
            "result": result,
        }

    @mcp.tool()
    def get_content_types_demo() -> list[TextContent | ImageContent | AudioContent]:
        """
        Demonstrate multiple content types in a single response.
        
        Returns a list containing text, image, and audio content to showcase
        the API's capability to handle diverse content types.
        """
        return [
            TextContent(
                type="text",
                text="This response demonstrates multiple content types supported by the API.",
            ),
            ImageContent(
                type="image",
                data=TEST_IMAGE_BASE64,
                mimeType="image/png",
            ),
            AudioContent(
                type="audio",
                data=TEST_AUDIO_BASE64,
                mimeType="audio/wav",
            ),
        ]

    @mcp.tool()
    async def tool_with_progress(ctx: Context[ServerSession, None]) -> str:
        """
        Demonstrate progress reporting during long-running operations.
        
        This tool simulates a multi-step process and reports progress
        at each stage, useful for tracking long-running tasks.
        """
        await ctx.report_progress(progress=0, total=100, message="Starting operation")
        await asyncio.sleep(0.1)
        
        await ctx.report_progress(progress=50, total=100, message="Processing data")
        await asyncio.sleep(0.1)
        
        await ctx.report_progress(progress=100, total=100, message="Operation complete")
        
        return "Operation completed successfully with progress tracking"

    # ========== RESOURCES ==========
    @mcp.resource("tech://api/status")
    def api_status_resource() -> str:
        """
        API status resource providing real-time server health information.
        """
        status_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "authenticated": True,
        }
        return json.dumps(status_data, indent=2)

    @mcp.resource("tech://api/documentation")
    def api_documentation_resource() -> str:
        """
        Comprehensive API documentation resource.
        """
        docs = """
        # MCP Technology Models API Documentation
        
        ## Overview
        This API provides comprehensive access to all MCP technology models with secure authentication.
        
        ## Features
        - OAuth 2.0 Authentication
        - RESTful API Design
        - Multiple Content Types Support
        - Real-time Progress Tracking
        - Comprehensive Error Handling
        
        ## Endpoints
        - Tools: Execute various operations and get system information
        - Resources: Access server data and documentation
        - Prompts: Generate contextual prompts for AI interactions
        - Completions: Get intelligent suggestions and completions
        
        ## Authentication
        All requests require OAuth 2.0 authentication with the 'mcp' scope.
        """
        return docs

    @mcp.resource("tech://data/template/{id}")
    def template_resource(id: str) -> str:
        """
        Template resource with dynamic parameter substitution.
        
        Args:
            id: Resource identifier
        """
        data = {
            "id": id,
            "type": "template_resource",
            "generated_at": time.time(),
            "data": f"This is dynamic content for resource ID: {id}",
        }
        return json.dumps(data, indent=2)

    @mcp.resource("tech://binary/image")
    def binary_image_resource() -> bytes:
        """
        Binary resource providing image data.
        """
        return base64.b64decode(TEST_IMAGE_BASE64)

    # ========== PROMPTS ==========
    @mcp.prompt()
    def system_analysis_prompt() -> list[UserMessage]:
        """
        Generate a prompt for analyzing system status and performance.
        """
        return [
            UserMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        "Analyze the current system status, performance metrics, "
                        "and provide recommendations for optimization."
                    ),
                ),
            )
        ]

    @mcp.prompt()
    def data_query_prompt(query: str, format: str = "json") -> list[UserMessage]:
        """
        Generate a prompt for querying data with specific format.
        
        Args:
            query: The data query to execute
            format: Output format (json, csv, xml)
        """
        return [
            UserMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"Execute the following query and return results in {format} format:\n\n{query}",
                ),
            )
        ]

    @mcp.prompt()
    def multimodal_analysis_prompt() -> list[UserMessage]:
        """
        Generate a prompt for multimodal content analysis.
        """
        return [
            UserMessage(
                role="user",
                content=ImageContent(
                    type="image",
                    data=TEST_IMAGE_BASE64,
                    mimeType="image/png",
                ),
            ),
            UserMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="Analyze the provided image and describe its contents, structure, and any notable features.",
                ),
            ),
        ]

    # ========== COMPLETIONS ==========
    @mcp.completion()
    async def handle_completion(
        ref: PromptReference | ResourceTemplateReference,
        argument: CompletionArgument,
        context: CompletionContext | None,
    ) -> Completion:
        """
        Provide intelligent completions for prompts and resources.
        
        This handler suggests appropriate values based on the context
        and argument being completed.
        """
        # Example completions for different argument names
        completion_suggestions: dict[str, list[str]] = {
            "format": ["json", "csv", "xml", "yaml"],
            "operation": ["add", "subtract", "multiply", "divide"],
            "id": ["123", "456", "789", "abc", "xyz"],
            "query": ["SELECT * FROM data", "UPDATE status SET value = 1", "DELETE FROM cache"],
        }
        
        suggestions = completion_suggestions.get(argument.name, [])
        
        # Filter suggestions based on current value
        if argument.value:
            suggestions = [s for s in suggestions if s.startswith(argument.value)]
        
        return Completion(
            values=suggestions,
            total=len(suggestions),
            hasMore=False,
        )

    return mcp


@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=8000, help="Port to listen on")
@click.option("--transport", default="streamable-http", type=click.Choice(["streamable-http", "sse"]),
              help="Transport protocol to use")
def main(host: str, port: int, transport: str) -> int:
    """
    Run the MCP Technology Models API Server.
    
    This server provides a comprehensive demonstration of all MCP technology models
    (tools, resources, prompts, completions) with secure OAuth authentication.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    auth_settings = TechModelAuthSettings()
    
    server = create_tech_models_api_server(host, port, auth_settings)
    
    logger.info(f"🔥 MCP Technology Models API Server starting on http://{host}:{port}")
    logger.info(f"📚 API endpoint: http://{host}:{port}/mcp")
    logger.info(
        f"🔐 Demo credentials - Username: {auth_settings.demo_username}, "
        f"Password: {auth_settings.demo_password}"
    )
    
    server.run(transport=transport)
    
    return 0


if __name__ == "__main__":
    main()
