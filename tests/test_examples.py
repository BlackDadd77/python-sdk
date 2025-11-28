"""Tests for example servers"""
# TODO(Marcelo): The `examples` directory needs to be importable as a package.
# pyright: reportMissingImports=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false

import sys

import pytest
from pytest_examples import CodeExample, EvalExample, find_examples

from mcp.shared.memory import create_connected_server_and_client_session as client_session
from mcp.types import TextContent, TextResourceContents


@pytest.mark.anyio
async def test_simple_echo():
    """Test the simple echo server"""
    from examples.fastmcp.simple_echo import mcp

    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("echo", {"text": "hello"})
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert content.text == "hello"


@pytest.mark.anyio
async def test_complex_inputs():
    """Test the complex inputs server"""
    from examples.fastmcp.complex_inputs import mcp

    async with client_session(mcp._mcp_server) as client:
        tank = {"shrimp": [{"name": "bob"}, {"name": "alice"}]}
        result = await client.call_tool("name_shrimp", {"tank": tank, "extra_names": ["charlie"]})
        assert len(result.content) == 3
        assert isinstance(result.content[0], TextContent)
        assert isinstance(result.content[1], TextContent)
        assert isinstance(result.content[2], TextContent)
        assert result.content[0].text == "bob"
        assert result.content[1].text == "alice"
        assert result.content[2].text == "charlie"


@pytest.mark.anyio
async def test_direct_call_tool_result_return():
    """Test the CallToolResult echo server"""
    from examples.fastmcp.direct_call_tool_result_return import mcp

    async with client_session(mcp._mcp_server) as client:
        result = await client.call_tool("echo", {"text": "hello"})
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert content.text == "hello"
        assert result.structuredContent
        assert result.structuredContent["text"] == "hello"
        assert isinstance(result.meta, dict)
        assert result.meta["some"] == "metadata"


@pytest.mark.anyio
async def test_desktop(monkeypatch: pytest.MonkeyPatch):
    """Test the desktop server"""
    from pathlib import Path

    from pydantic import AnyUrl

    from examples.fastmcp.desktop import mcp

    # Mock desktop directory listing
    mock_files = [Path("/fake/path/file1.txt"), Path("/fake/path/file2.txt")]
    monkeypatch.setattr(Path, "iterdir", lambda self: mock_files)  # type: ignore[reportUnknownArgumentType]
    monkeypatch.setattr(Path, "home", lambda: Path("/fake/home"))

    async with client_session(mcp._mcp_server) as client:
        # Test the sum function
        result = await client.call_tool("sum", {"a": 1, "b": 2})
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert content.text == "3"

        # Test the desktop resource
        result = await client.read_resource(AnyUrl("dir://desktop"))
        assert len(result.contents) == 1
        content = result.contents[0]
        assert isinstance(content, TextResourceContents)
        assert isinstance(content.text, str)
        if sys.platform == "win32":  # pragma: no cover
            file_1 = "/fake/path/file1.txt".replace("/", "\\\\")  # might be a bug
            file_2 = "/fake/path/file2.txt".replace("/", "\\\\")  # might be a bug
            assert file_1 in content.text
            assert file_2 in content.text
            # might be a bug, but the test is passing
        else:  # pragma: no cover
            assert "/fake/path/file1.txt" in content.text
            assert "/fake/path/file2.txt" in content.text


@pytest.mark.parametrize("example", find_examples("README.md"), ids=str)
def test_docs_examples(example: CodeExample, eval_example: EvalExample):
    ruff_ignore: list[str] = ["F841", "I001", "F821"]  # F821: undefined names (snippets lack imports)

    # Use project's actual line length of 120
    eval_example.set_config(ruff_ignore=ruff_ignore, target_version="py310", line_length=120)

    # Use Ruff for both formatting and linting (skip Black)
    if eval_example.update_examples:  # pragma: no cover
        eval_example.format_ruff(example)
    else:
        eval_example.lint_ruff(example)


@pytest.mark.anyio
async def test_bank_data_create_account():
    """Test the bank data server - create account functionality"""
    from examples.fastmcp.bank_data import _accounts, _transaction_counter, mcp

    # Reset state for test isolation
    _accounts.clear()
    _transaction_counter[0] = 0

    async with client_session(mcp._mcp_server) as client:
        # Create an account with initial deposit
        result = await client.call_tool("create_account", {"name": "John Doe", "initial_deposit": 100.0})
        assert len(result.content) == 1
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert "Account created successfully" in content.text
        assert "ACC000001" in content.text
        assert "$100.00" in content.text


@pytest.mark.anyio
async def test_bank_data_deposit_and_withdraw():
    """Test the bank data server - deposit and withdrawal functionality"""
    from examples.fastmcp.bank_data import _accounts, _transaction_counter, mcp

    # Reset state for test isolation
    _accounts.clear()
    _transaction_counter[0] = 0

    async with client_session(mcp._mcp_server) as client:
        # Create an account
        await client.call_tool("create_account", {"name": "Jane Smith", "initial_deposit": 50.0})

        # Deposit money
        result = await client.call_tool("deposit", {"account_id": "ACC000001", "amount": 25.0})
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert "Deposited $25.00" in content.text
        assert "New balance: $75.00" in content.text

        # Withdraw money
        result = await client.call_tool("withdraw", {"account_id": "ACC000001", "amount": 20.0})
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert "Withdrew $20.00" in content.text
        assert "New balance: $55.00" in content.text


@pytest.mark.anyio
async def test_bank_data_transfer():
    """Test the bank data server - transfer functionality"""
    from examples.fastmcp.bank_data import _accounts, _transaction_counter, mcp

    # Reset state for test isolation
    _accounts.clear()
    _transaction_counter[0] = 0

    async with client_session(mcp._mcp_server) as client:
        # Create two accounts
        await client.call_tool("create_account", {"name": "Alice", "initial_deposit": 100.0})
        await client.call_tool("create_account", {"name": "Bob", "initial_deposit": 50.0})

        # Transfer money
        result = await client.call_tool(
            "transfer", {"from_account_id": "ACC000001", "to_account_id": "ACC000002", "amount": 30.0}
        )
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert "Transferred $30.00" in content.text
        assert "Source balance: $70.00" in content.text
        assert "Destination balance: $80.00" in content.text


@pytest.mark.anyio
async def test_bank_data_insufficient_funds():
    """Test the bank data server - insufficient funds error"""
    from examples.fastmcp.bank_data import _accounts, _transaction_counter, mcp

    # Reset state for test isolation
    _accounts.clear()
    _transaction_counter[0] = 0

    async with client_session(mcp._mcp_server) as client:
        # Create an account with small balance
        await client.call_tool("create_account", {"name": "Test User", "initial_deposit": 10.0})

        # Try to withdraw more than available
        result = await client.call_tool("withdraw", {"account_id": "ACC000001", "amount": 50.0})
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert "Error: Insufficient funds" in content.text
