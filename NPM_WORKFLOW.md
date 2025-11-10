# NPM Workflow for MCP Python SDK

This document describes how to use npm commands as an alternative workflow for building, testing, and deploying the MCP Python SDK.

## Prerequisites

Before using the npm workflow, ensure you have:

1. **Node.js and npm** installed (Node.js >= 18.0.0, npm >= 9.0.0)
2. **uv** installed - [Installation instructions](https://docs.astral.sh/uv/)
3. **Python** >= 3.10

## Quick Start

```bash
# Install Python dependencies
npm install

# Build documentation
npm run build

# Deploy documentation to GitHub Pages
npm run deploy
```

## Available Commands

### Installation

```bash
npm install
```
Installs all Python dependencies using `uv sync --frozen`.

### Building

```bash
npm run build
```
Builds the documentation using MkDocs. Output is generated in the `site/` directory.

### Deployment

```bash
npm run deploy
```
Deploys the built documentation to GitHub Pages using `mkdocs gh-deploy`.

### Testing

```bash
npm test
```
Runs the full test suite using pytest.

### Linting

```bash
npm run lint
```
Runs ruff linter to check code quality.

### Formatting

```bash
# Format code
npm run format

# Check formatting without making changes
npm run format:check
```
Uses ruff to format Python code according to project standards.

### Type Checking

```bash
npm run typecheck
```
Runs pyright for static type checking.

### Development Server

```bash
npm run dev
```
Starts a local development server for documentation at http://127.0.0.1:8000.

### Pre-commit Checks

```bash
npm run pre-commit
```
Runs all pre-commit hooks to validate code before committing.

### Cleaning

```bash
npm run clean
```
Removes build artifacts and cache directories.

## Workflow Examples

### Standard Development Workflow

```bash
# 1. Install dependencies
npm install

# 2. Make your changes to the code

# 3. Format and lint
npm run format
npm run lint

# 4. Type check
npm run typecheck

# 5. Run tests
npm test

# 6. Run pre-commit checks
npm run pre-commit
```

### Documentation Workflow

```bash
# 1. Install dependencies
npm install

# 2. Start development server
npm run dev

# 3. Make changes to documentation in docs/

# 4. Build documentation
npm run build

# 5. Deploy to GitHub Pages (if you have permissions)
npm run deploy
```

## Why npm?

While this is a Python project that uses `uv` for package management, npm provides:

1. **Familiar interface** for developers coming from JavaScript/TypeScript backgrounds
2. **Unified commands** across different projects
3. **Easy integration** with CI/CD pipelines that already use npm
4. **Simplified onboarding** with a consistent `npm install`, `npm run build`, `npm run deploy` pattern

## Troubleshooting

### "uv: command not found"

If you see this error, you need to install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Permission Issues with Deploy

The `npm run deploy` command requires push access to the repository's `gh-pages` branch. Ensure you have the necessary permissions.

### Build Failures

If builds fail, try cleaning first:
```bash
npm run clean
npm install
npm run build
```

## Alternative: Using uv Directly

If you prefer to use uv directly without npm:

```bash
# Install dependencies
uv sync --frozen

# Run tests
uv run --frozen --no-sync pytest

# Build docs
uv run --frozen --no-sync mkdocs build

# Deploy docs
uv run --frozen --no-sync mkdocs gh-deploy --force
```

See the main [README.md](README.md) for comprehensive documentation on using uv directly.
