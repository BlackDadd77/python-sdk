#!/bin/bash
set -e
echo "🚀 Building project..."
mkdir -p dist
cp index.html dist/
cp -r src dist/
echo "✅ Build complete."
