#!/bin/bash
#
# Sonic Forage Autonomous Session Entrypoint
#
# Supports scheduled "shows":
#   - SHOW_TIME=20:00   (24h format)
#   - BOOT_EARLY_MINUTES=30
#
# Example usage (via docker-compose or host cron):
#   docker run ... -e SHOW_TIME="20:00" -e BOOT_EARLY_MINUTES=45 forage-dj swarm-distribute ...
#
# The container will:
#   1. Wait until (SHOW_TIME - BOOT_EARLY_MINUTES)
#   2. Run full system prep (doctor, model loading hints)
#   3. Execute the requested autonomous command (generate setlist, run live mode, swarm distribution, etc.)
#   4. Stay alive or exit cleanly after the performance window

set -euo pipefail

echo "🌊 Sonic Forage Autonomous Session Starting"
echo "Current time: $(date)"
echo "Project root inside container: /workspace/forage-dj"

# Activate environment
source /workspace/forage-dj/.venv/bin/activate 2>/dev/null || true

# Default behavior if no scheduling env vars are set
if [ -z "${SHOW_TIME:-}" ]; then
    echo "No SHOW_TIME set - running immediately in interactive/autonomous mode."
    exec "$@"
fi

# Parse SHOW_TIME (HH:MM)
IFS=: read -r show_hour show_min <<< "$SHOW_TIME"
show_epoch=$(date -d "today $show_hour:$show_min" +%s 2>/dev/null || date -d "$SHOW_TIME" +%s)

BOOT_EARLY_MINUTES=${BOOT_EARLY_MINUTES:-30}
target_epoch=$(( show_epoch - BOOT_EARLY_MINUTES * 60 ))
now=$(date +%s)

if [ "$now" -lt "$target_epoch" ]; then
    sleep_seconds=$(( target_epoch - now ))
    echo "Scheduled show at $SHOW_TIME"
    echo "Booting early by ${BOOT_EARLY_MINUTES} minutes for model loading + generation."
    echo "Sleeping for $((sleep_seconds / 60)) minutes..."
    sleep "$sleep_seconds"
fi

echo "=== BOOT WINDOW REACHED ==="
echo "Running full system preparation (doctor + rave-prep style checks)..."
uv run foragedj doctor --heal || true
uv run foragedj rave-prep || true

echo "=== STARTING AUTONOMOUS PERFORMANCE ==="
echo "Executing: $@"
echo ""

# Run the actual autonomous command the user scheduled
# Examples the user can pass:
#   swarm-distribute --input sessions/TonightSet --mode full --seed-bomb
#   generate-setlist --manifest setlists/saturday_night.yaml
#   live --manifest setlists/saturday_night.yaml --lookahead 2
exec "$@"

# After the command finishes (e.g. a 2-hour live set ends), the container can exit
# or you can add post-show logic here (export recordings, upload seeds, etc.)
echo "=== PERFORMANCE WINDOW COMPLETE ==="
echo "Autonomous session finished at $(date)"