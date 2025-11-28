"""Tests for the MCP Technology Models API Server."""

import pytest
from mcp_tech_models_api.server import TechModelAuthSettings, create_tech_models_api_server


class TestTechModelsAPIServer:
    """Test suite for the Technology Models API Server."""

    @pytest.fixture
    def auth_settings(self):
        """Create auth settings for testing."""
        return TechModelAuthSettings(
            mcp_scope="mcp",
            demo_username="test_user",
            demo_password="test_pass",
        )

    @pytest.fixture
    def server(self, auth_settings):
        """Create a test server instance."""
        return create_tech_models_api_server(
            host="localhost",
            port=8888,
            auth_settings=auth_settings,
        )

    def test_server_creation(self, server):
        """Test that the server can be created successfully."""
        assert server is not None
        assert server.name == "MCP Technology Models API"

    def test_server_has_mcp_server(self, server):
        """Test that the server has an internal MCP server."""
        assert hasattr(server, '_mcp_server')
        assert server._mcp_server is not None

    def test_server_auth_enabled(self, server):
        """Test that authentication is enabled on the server."""
        # Verify the server has auth provider configured (private attr)
        assert hasattr(server, '_auth_server_provider')
        assert server._auth_server_provider is not None

    def test_server_settings(self, server):
        """Test server settings are configured correctly."""
        assert server.settings is not None
        assert server.settings.host == "localhost"
        assert server.settings.port == 8888

    def test_auth_settings(self, auth_settings):
        """Test authentication settings."""
        assert auth_settings.mcp_scope == "mcp"
        assert auth_settings.demo_username == "test_user"
        assert auth_settings.demo_password == "test_pass"

    @pytest.mark.anyio
    async def test_oauth_provider_login_page(self, auth_settings):
        """Test OAuth provider login page generation."""
        from mcp_tech_models_api.server import TechModelOAuthProvider
        
        provider = TechModelOAuthProvider(
            auth_settings=auth_settings,
            auth_callback_path="http://localhost:8888/login/callback",
            server_url="http://localhost:8888",
        )
        
        response = await provider.get_login_page("test_state")
        assert response is not None
        assert response.status_code == 200
        assert "text/html" in response.media_type
        
        # Check that the HTML contains expected elements
        content = response.body.decode()
        assert "Tech Models API" in content
        assert "test_state" in content
        assert auth_settings.demo_username in content

    @pytest.mark.anyio
    async def test_oauth_provider_create_client(self, auth_settings):
        """Test OAuth client creation."""
        from mcp_tech_models_api.server import TechModelOAuthProvider
        from pydantic import AnyHttpUrl
        
        provider = TechModelOAuthProvider(
            auth_settings=auth_settings,
            auth_callback_path="http://localhost:8888/login/callback",
            server_url="http://localhost:8888",
        )
        
        client_id, client_secret = await provider.create_client(
            client_name="Test Client",
            redirect_uris=[AnyHttpUrl("http://localhost:8080/callback")],
            scopes=["mcp"],
        )
        
        assert client_id is not None
        assert client_secret is not None
        assert client_id.startswith("client_")
        
        # Verify client can be retrieved
        client = await provider.get_client(client_id)
        assert client is not None
        assert client["client_id"] == client_id
        assert client["client_name"] == "Test Client"

    @pytest.mark.anyio
    async def test_oauth_provider_validate_credentials(self, auth_settings):
        """Test OAuth client credential validation."""
        from mcp_tech_models_api.server import TechModelOAuthProvider
        from pydantic import AnyHttpUrl
        
        provider = TechModelOAuthProvider(
            auth_settings=auth_settings,
            auth_callback_path="http://localhost:8888/login/callback",
            server_url="http://localhost:8888",
        )
        
        client_id, client_secret = await provider.create_client(
            client_name="Test Client",
            redirect_uris=[AnyHttpUrl("http://localhost:8080/callback")],
            scopes=["mcp"],
        )
        
        # Test valid credentials
        is_valid = await provider.validate_client_secret(client_id, client_secret)
        assert is_valid is True
        
        # Test invalid credentials
        is_valid = await provider.validate_client_secret(client_id, "wrong_secret")
        assert is_valid is False

    @pytest.mark.anyio
    async def test_oauth_provider_authorization_code_flow(self, auth_settings):
        """Test OAuth authorization code flow."""
        from mcp_tech_models_api.server import TechModelOAuthProvider
        from pydantic import AnyHttpUrl
        
        provider = TechModelOAuthProvider(
            auth_settings=auth_settings,
            auth_callback_path="http://localhost:8888/login/callback",
            server_url="http://localhost:8888",
        )
        
        client_id, _ = await provider.create_client(
            client_name="Test Client",
            redirect_uris=[AnyHttpUrl("http://localhost:8080/callback")],
            scopes=["mcp"],
        )
        
        # Create authorization code
        redirect_uri = "http://localhost:8080/callback"
        auth_code = await provider.create_authorization_code(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scopes=["mcp"],
        )
        
        assert auth_code is not None
        
        # Validate authorization code
        code_data = await provider.validate_authorization_code(
            client_id=client_id,
            code=auth_code,
            redirect_uri=redirect_uri,
        )
        
        assert code_data is not None
        assert code_data["client_id"] == client_id
        assert code_data["redirect_uri"] == redirect_uri
        assert "mcp" in code_data["scopes"]

    @pytest.mark.anyio
    async def test_oauth_provider_token_lifecycle(self, auth_settings):
        """Test OAuth token creation, validation, and revocation."""
        from mcp_tech_models_api.server import TechModelOAuthProvider
        from pydantic import AnyHttpUrl
        
        provider = TechModelOAuthProvider(
            auth_settings=auth_settings,
            auth_callback_path="http://localhost:8888/login/callback",
            server_url="http://localhost:8888",
        )
        
        client_id, _ = await provider.create_client(
            client_name="Test Client",
            redirect_uris=[AnyHttpUrl("http://localhost:8080/callback")],
            scopes=["mcp"],
        )
        
        # Create access token
        access_token, expires_in = await provider.create_access_token(
            client_id=client_id,
            scopes=["mcp"],
        )
        
        assert access_token is not None
        assert expires_in > 0
        
        # Validate token
        token_data = await provider.load_access_token(access_token)
        assert token_data is not None
        assert token_data.client_id == client_id
        
        # Create refresh token
        refresh_token = await provider.create_refresh_token(
            client_id=client_id,
            scopes=["mcp"],
        )
        
        assert refresh_token is not None
        
        # Revoke access token
        revoked = await provider.revoke_token(access_token)
        assert revoked is True
        
        # Verify token is revoked
        token_data = await provider.load_access_token(access_token)
        assert token_data is None


class TestTechModelsAPIIntegration:
    """Integration tests for the Technology Models API Server."""

    @pytest.fixture
    def server(self):
        """Create a test server for integration tests."""
        auth_settings = TechModelAuthSettings(
            mcp_scope="mcp",
            demo_username="test_user",
            demo_password="test_pass",
        )
        return create_tech_models_api_server(
            host="localhost",
            port=8889,
            auth_settings=auth_settings,
        )

    def test_server_can_be_created_for_integration(self, server):
        """Test that a server can be created for integration testing."""
        assert server is not None
        assert server._mcp_server is not None

