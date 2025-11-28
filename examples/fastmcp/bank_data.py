"""
FastMCP Bank Data Server

A demonstration of bank data management using FastMCP.
Provides tools for account management, transactions, and balance inquiries.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from pydantic import Field

from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("Bank Data Server")


@dataclass
class Transaction:
    """Represents a bank transaction."""

    id: str
    account_id: str
    amount: Decimal
    transaction_type: str  # "deposit", "withdrawal", "transfer_in", "transfer_out"
    timestamp: datetime
    description: str


@dataclass
class Account:
    """Represents a bank account."""

    id: str
    name: str
    balance: Decimal = field(default_factory=lambda: Decimal("0.00"))
    transactions: list["Transaction"] = field(default_factory=lambda: [])
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# In-memory storage for demonstration purposes
_accounts: dict[str, Account] = {}
_transaction_counter: list[int] = [0]  # Using list to avoid global statement


def _generate_transaction_id() -> str:
    """Generate a unique transaction ID."""
    _transaction_counter[0] += 1
    return f"TXN{_transaction_counter[0]:06d}"


def _generate_account_id() -> str:
    """Generate a unique account ID."""
    return f"ACC{len(_accounts) + 1:06d}"


# ===== Tools for Account Management =====


@mcp.tool()
def create_account(
    name: Annotated[str, Field(description="Name of the account holder")],
    initial_deposit: Annotated[float, Field(description="Initial deposit amount", ge=0)] = 0.0,
) -> str:
    """Create a new bank account with an optional initial deposit."""
    account_id = _generate_account_id()
    account = Account(
        id=account_id,
        name=name,
        balance=Decimal(str(initial_deposit)),
    )

    if initial_deposit > 0:
        transaction = Transaction(
            id=_generate_transaction_id(),
            account_id=account_id,
            amount=Decimal(str(initial_deposit)),
            transaction_type="deposit",
            timestamp=datetime.now(timezone.utc),
            description="Initial deposit",
        )
        account.transactions.append(transaction)

    _accounts[account_id] = account
    return f"Account created successfully. Account ID: {account_id}, Balance: ${account.balance:.2f}"


@mcp.tool()
def get_account_info(
    account_id: Annotated[str, Field(description="The account ID to retrieve")],
) -> str:
    """Get detailed information about a bank account."""
    if account_id not in _accounts:
        return f"Error: Account {account_id} not found."

    account = _accounts[account_id]
    return (
        f"Account ID: {account.id}\n"
        f"Name: {account.name}\n"
        f"Balance: ${account.balance:.2f}\n"
        f"Created: {account.created_at.isoformat()}\n"
        f"Transaction count: {len(account.transactions)}"
    )


@mcp.tool()
def list_accounts() -> str:
    """List all bank accounts."""
    if not _accounts:
        return "No accounts found."

    account_lines = [f"  {account.id}: {account.name} - ${account.balance:.2f}" for account in _accounts.values()]
    return "\n".join(["Account List:", "-" * 40, *account_lines])


@mcp.tool()
def close_account(
    account_id: Annotated[str, Field(description="The account ID to close")],
) -> str:
    """Close a bank account. Account must have zero balance."""
    if account_id not in _accounts:
        return f"Error: Account {account_id} not found."

    account = _accounts[account_id]
    if account.balance != Decimal("0.00"):
        return f"Error: Cannot close account with balance ${account.balance:.2f}. Please withdraw all funds first."

    del _accounts[account_id]
    return f"Account {account_id} has been closed successfully."


# ===== Tools for Transactions =====


@mcp.tool()
def deposit(
    account_id: Annotated[str, Field(description="The account ID to deposit into")],
    amount: Annotated[float, Field(description="Amount to deposit", gt=0)],
    description: Annotated[str, Field(description="Transaction description")] = "Deposit",
) -> str:
    """Deposit money into a bank account."""
    if account_id not in _accounts:
        return f"Error: Account {account_id} not found."

    account = _accounts[account_id]
    deposit_amount = Decimal(str(amount))

    transaction = Transaction(
        id=_generate_transaction_id(),
        account_id=account_id,
        amount=deposit_amount,
        transaction_type="deposit",
        timestamp=datetime.now(timezone.utc),
        description=description,
    )

    account.balance += deposit_amount
    account.transactions.append(transaction)

    return f"Deposited ${deposit_amount:.2f} to {account_id}. New balance: ${account.balance:.2f}"


@mcp.tool()
def withdraw(
    account_id: Annotated[str, Field(description="The account ID to withdraw from")],
    amount: Annotated[float, Field(description="Amount to withdraw", gt=0)],
    description: Annotated[str, Field(description="Transaction description")] = "Withdrawal",
) -> str:
    """Withdraw money from a bank account."""
    if account_id not in _accounts:
        return f"Error: Account {account_id} not found."

    account = _accounts[account_id]
    withdrawal_amount = Decimal(str(amount))

    if account.balance < withdrawal_amount:
        return f"Error: Insufficient funds. Available balance: ${account.balance:.2f}"

    transaction = Transaction(
        id=_generate_transaction_id(),
        account_id=account_id,
        amount=withdrawal_amount,
        transaction_type="withdrawal",
        timestamp=datetime.now(timezone.utc),
        description=description,
    )

    account.balance -= withdrawal_amount
    account.transactions.append(transaction)

    return f"Withdrew ${withdrawal_amount:.2f} from {account_id}. New balance: ${account.balance:.2f}"


@mcp.tool()
def transfer(
    from_account_id: Annotated[str, Field(description="The source account ID")],
    to_account_id: Annotated[str, Field(description="The destination account ID")],
    amount: Annotated[float, Field(description="Amount to transfer", gt=0)],
    description: Annotated[str, Field(description="Transfer description")] = "Transfer",
) -> str:
    """Transfer money between two bank accounts."""
    if from_account_id not in _accounts:
        return f"Error: Source account {from_account_id} not found."
    if to_account_id not in _accounts:
        return f"Error: Destination account {to_account_id} not found."
    if from_account_id == to_account_id:
        return "Error: Cannot transfer to the same account."

    from_account = _accounts[from_account_id]
    to_account = _accounts[to_account_id]
    transfer_amount = Decimal(str(amount))

    if from_account.balance < transfer_amount:
        return f"Error: Insufficient funds. Available balance: ${from_account.balance:.2f}"

    timestamp = datetime.now(timezone.utc)

    # Create outgoing transaction
    out_transaction = Transaction(
        id=_generate_transaction_id(),
        account_id=from_account_id,
        amount=transfer_amount,
        transaction_type="transfer_out",
        timestamp=timestamp,
        description=f"{description} to {to_account_id}",
    )

    # Create incoming transaction
    in_transaction = Transaction(
        id=_generate_transaction_id(),
        account_id=to_account_id,
        amount=transfer_amount,
        transaction_type="transfer_in",
        timestamp=timestamp,
        description=f"{description} from {from_account_id}",
    )

    from_account.balance -= transfer_amount
    to_account.balance += transfer_amount
    from_account.transactions.append(out_transaction)
    to_account.transactions.append(in_transaction)

    return (
        f"Transferred ${transfer_amount:.2f} from {from_account_id} to {to_account_id}.\n"
        f"Source balance: ${from_account.balance:.2f}\n"
        f"Destination balance: ${to_account.balance:.2f}"
    )


@mcp.tool()
def get_transaction_history(
    account_id: Annotated[str, Field(description="The account ID to get history for")],
    limit: Annotated[int, Field(description="Maximum number of transactions to return", ge=1, le=100)] = 10,
) -> str:
    """Get the transaction history for a bank account."""
    if account_id not in _accounts:
        return f"Error: Account {account_id} not found."

    account = _accounts[account_id]
    transactions = account.transactions[-limit:]

    if not transactions:
        return f"No transactions found for account {account_id}."

    lines = [f"Transaction History for {account_id}:", "-" * 50]
    for txn in reversed(transactions):
        sign = "+" if txn.transaction_type in ("deposit", "transfer_in") else "-"
        lines.append(f"  {txn.timestamp.strftime('%Y-%m-%d %H:%M')} | {sign}${txn.amount:.2f} | {txn.description}")
    lines.append("-" * 50)
    lines.append(f"Current Balance: ${account.balance:.2f}")

    return "\n".join(lines)


# ===== Resources =====


@mcp.resource("bank://accounts")
def list_all_accounts() -> str:
    """Get a list of all bank accounts as a resource."""
    if not _accounts:
        return "No accounts available."

    lines = [f"{account.id}: {account.name} (${account.balance:.2f})" for account in _accounts.values()]
    return "\n".join(lines)


@mcp.resource("bank://account/{account_id}")
def get_account_resource(account_id: str) -> str:
    """Get details of a specific bank account as a resource."""
    if account_id not in _accounts:
        return f"Account {account_id} not found."

    account = _accounts[account_id]
    return (
        f"Account: {account.id}\n"
        f"Holder: {account.name}\n"
        f"Balance: ${account.balance:.2f}\n"
        f"Opened: {account.created_at.strftime('%Y-%m-%d')}"
    )


@mcp.resource("bank://account/{account_id}/balance")
def get_balance_resource(account_id: str) -> str:
    """Get just the balance of an account as a resource."""
    if account_id not in _accounts:
        return "0.00"
    return str(_accounts[account_id].balance)


# ===== Prompts =====


@mcp.prompt("open_account")
def open_account_prompt(name: str, initial_deposit: str = "0") -> str:
    """Prompt template for opening a new bank account."""
    return f"Please open a new bank account for {name} with an initial deposit of ${initial_deposit}."


@mcp.prompt("check_balance")
def check_balance_prompt(account_id: str) -> str:
    """Prompt template for checking account balance."""
    return f"Please check the balance for account {account_id}."


@mcp.prompt("make_transfer")
def make_transfer_prompt(from_account: str, to_account: str, amount: str) -> str:
    """Prompt template for making a transfer between accounts."""
    return f"Please transfer ${amount} from account {from_account} to account {to_account}."


if __name__ == "__main__":
    mcp.run()
