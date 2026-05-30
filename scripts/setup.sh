#!/usr/bin/env bash
# forage-dj Linux / macOS / WSL Easy Installer
#
# Preferred for most users (Linux and Windows):
#   python scripts/install.py            # universal cross-platform (recommended)
#   python scripts/install.py --full
#
# This script is now a thin convenience wrapper around the universal installer.
# It keeps the old Linux audio package logic for convenience.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

MODE="cpu"

usage() {
    cat <<EOF
forage-dj setup.sh (Linux/mac convenience wrapper)

Recommended for all platforms:
  python scripts/install.py
  python scripts/install.py --full

This script now mostly calls the universal Python installer.

Options (passed through):
  --full    Install all extras
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --full) MODE="full"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown arg: $1"; usage; exit 1 ;;
    esac
done

echo "🎧 forage-dj Linux/mac setup (delegating to universal installer)"
echo "   For the best cross-platform experience use: python scripts/install.py"

# Legacy Linux audio packages (optional but helpful)
if [[ "$(uname -s)" == "Linux" ]] && command -v apt-get >/dev/null 2>&1; then
    echo "→ Installing common Linux audio dev packages (you can skip with Ctrl-C)..."
    sudo apt-get update -qq || true
    sudo apt-get install -y -qq \
        libportaudio2 portaudio19-dev ffmpeg espeak-ng \
        libsndfile1 build-essential python3-dev 2>/dev/null || true
fi

# Delegate to the real cross-platform logic
if [[ "$MODE" == "full" ]]; then
    python scripts/install.py --full
else
    python scripts/install.py
fi

echo ""
echo "Tip: next time just run 'python scripts/install.py' (works on Windows too)"
