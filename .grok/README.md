# .grok/ — Grok Session State (Local to This Repo)

This directory lives inside the master repo at `/mnt/z/IMF2045/forage-dj`.

**Purpose**: Keep all Grok-related working notes, plans, swarm logs, and session artifacts co-located with the code on the large drive so you can easily read, edit, and version them.

## What's Here

- `PLAN.md` — Full detailed session plan (review + uv env fix + improvements + swarm launch strategy). This is the **editable master copy**.
- `README.md` — This file (you are here).
- Future: `swarm-logs/`, `agent-outputs/`, `todo-state.json`, etc.

## Quick Commands (from project root)

```bash
# Read the current plan
cat .grok/PLAN.md | less

# Edit the plan directly
$EDITOR .grok/PLAN.md

# See current swarm coordination
cat docs/SWARM_STATUS.md
```

## .venv Location

The virtual environment is intentionally created at the project root:

```
/mnt/z/IMF2045/forage-dj/.venv
```

This ensures it lives on the drive with more space (as requested). All `uv run`, `uv sync`, etc. use this environment.

## Git & Cleanup

Recommended `.gitignore` additions (already partially handled):

```
.grok/tmp/
.grok/logs/
.grok/agent-outputs/
```

Keep `PLAN.md` and important notes committed so the whole team (and future agents) has context.

## For Future Grok Sessions

When starting new work on this repo, prefer creating/using files under `.grok/` inside the project instead of the global `~/.grok/sessions/...` location when possible. This keeps everything on the spacious drive and makes it trivial for humans to inspect and edit.

---
*Master repo: /mnt/z/IMF2045/forage-dj*
