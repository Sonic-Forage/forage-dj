#!/usr/bin/env bash
#
# Sonic Forage Full Project Backup Script
# Everything stays on the large mounted drive.
#
# Usage:
#   ./scripts/backup_forage_dj.sh
#
# This creates a timestamped tar.gz of the entire project (excluding .venv and .git for speed)
# and also rsyncs critical live data (sessions, generated, public, libraries, checkpoints).
#
# Recommended: Run this before any big tour leg or after major generative runs.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_ROOT="/mnt/z/IMF2045/forage-dj-backups"   # Change this if you have another safe spot on the same drive or external
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/forage-dj_${TIMESTAMP}"

echo "🌊 Sonic Forage Backup"
echo "Project root: $PROJECT_ROOT"
echo "Backup destination: $BACKUP_DIR"
echo ""

mkdir -p "$BACKUP_DIR"

echo "→ Creating full project archive (excluding venv + .git for speed)..."
tar --exclude='.venv' \
    --exclude='.git' \
    --exclude='*.pyc' \
    -czf "${BACKUP_DIR}/forage-dj-full-${TIMESTAMP}.tar.gz" \
    -C "$(dirname "$PROJECT_ROOT")" \
    "$(basename "$PROJECT_ROOT")"

echo "→ Rsyncing critical live data (sessions, generated, libraries, public seeds, checkpoints)..."
mkdir -p "${BACKUP_DIR}/live-data"
rsync -a --delete \
    --exclude='.venv' \
    --exclude='.git' \
    "$PROJECT_ROOT/sessions/"     "${BACKUP_DIR}/live-data/sessions/"     2>/dev/null || true
rsync -a --delete \
    "$PROJECT_ROOT/generated/"    "${BACKUP_DIR}/live-data/generated/"    2>/dev/null || true
rsync -a --delete \
    "$PROJECT_ROOT/libraries/"    "${BACKUP_DIR}/live-data/libraries/"    2>/dev/null || true
rsync -a --delete \
    "$PROJECT_ROOT/public/"       "${BACKUP_DIR}/live-data/public/"       2>/dev/null || true
rsync -a --delete \
    "$PROJECT_ROOT/checkpoints/"  "${BACKUP_DIR}/live-data/checkpoints/"  2>/dev/null || true

echo ""
echo "✅ Backup complete!"
echo "Full archive: ${BACKUP_DIR}/forage-dj-full-${TIMESTAMP}.tar.gz"
echo "Live data mirror: ${BACKUP_DIR}/live-data/"
echo ""
echo "Recommended: Copy the entire ${BACKUP_ROOT} folder to an external drive or another machine periodically."
echo "Stay safe. The mycelium is backed up."