#!/usr/bin/env bash
# QuizForge macOS Build Script
# Builds Tauri desktop application for macOS
# Usage: bash scripts/build-mac.sh

set -euo pipefail

echo "=== QuizForge macOS Build ==="

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Install from https://nodejs.org/"
    exit 1
fi
echo "Node.js: $(node --version)"

# Check Rust
if ! command -v rustc &> /dev/null; then
    echo "ERROR: Rust is not installed. Install from https://rustup.rs/"
    exit 1
fi
echo "Rust: $(rustc --version)"

# Navigate to project root
cd "$(dirname "$0")/.."

echo ""
echo "Installing npm dependencies..."
npm install

echo ""
echo "Building Tauri application..."
npm run tauri build

echo ""
echo "=== Build Complete ==="
echo "Installer is located in:"
echo "  src-tauri/target/release/bundle/dmg/"
echo "  src-tauri/target/release/bundle/macos/"
