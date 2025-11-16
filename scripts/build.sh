#!/bin/bash

# Exit on error
set -e

echo "Building documentation with MkDocs..."

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "Using uv to build documentation..."
    uv run --frozen mkdocs build
else
    echo "uv not found, trying mkdocs directly..."
    if command -v mkdocs &> /dev/null; then
        mkdocs build
    else
        echo "Error: Neither uv nor mkdocs found. Please install one of them."
        exit 1
    fi
fi

# Copy site to dist directory for gh-pages deployment
echo "Copying site to dist directory..."
rm -rf dist
cp -r site dist

echo "Build complete! Documentation is available in the 'dist' directory."
