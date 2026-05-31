#!/bin/bash
# Launch Forage Radio TUI
# This will automatically install textual via uv if needed.

cd "$(dirname "$0")/../.."

echo "🎵 Starting Forage Radio TUI..."
echo "   (Scanning your ComfyUI output for generated tracks)"
echo ""

uv run --with textual python scripts/radio/forage_radio.py "$@"