#!/usr/bin/env bash
# QuizForge Web Build Script
# Builds the pure web frontend (no Tauri)
# Usage: bash scripts/build-web.sh

set -euo pipefail

echo "=== QuizForge Web Build ==="

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Install from https://nodejs.org/"
    exit 1
fi
echo "Node.js: $(node --version)"

# Navigate to project root
cd "$(dirname "$0")/.."

echo ""
echo "Installing npm dependencies..."
npm install

echo ""
echo "Building web frontend..."
npm run build

echo ""
echo "=== Build Complete ==="
echo "Output directory: dist/"
echo ""
echo "To preview locally:  npx vite preview"
echo "To deploy via Docker: docker compose up -d"
