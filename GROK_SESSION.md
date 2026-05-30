# Grok Session — forage-dj

**This is the master working session for the current Grok conversation.**

All important plans, decisions, and swarm coordination live here (and in `.grok/`) so everything is editable and stored on the large drive.

## Current Session

- **Detailed Plan**: [.grok/PLAN.md](.grok/PLAN.md) ← **Primary editable document**
- **Swarm Status**: [docs/SWARM_STATUS.md](docs/SWARM_STATUS.md)
- **Environment Guide**: See `.grok/README.md`

## Quick Start (after any clone)

```bash
./scripts/setup.sh
uv run foragedj doctor
```

## Why This Structure?

- The repo root (`/mnt/z/IMF2045/forage-dj`) is the single source of truth.
- `.venv` lives here (on the big drive).
- All Grok artifacts that humans need to read/edit are inside the repo.
- Easy to `git add .grok/PLAN.md` when the plan evolves.

Last updated: This session (Phase 0 complete + uv env working + initial swarm launched).

See the full history in `.grok/PLAN.md`.

## Latest Swarm Activity
- Previous phase (env + scaffolding + Audio Gen + Mixer/GUI agents) complete.
- **New planning session started**: Focused on model pre-downloads to `checkpoints/` on Z:, ONNX investigation, locked-seed Bass House setlist manifests (per official prompting guide), engine tests, and headless test swarm.

See the current plan at `.grok/PLAN.md` (editable copy in master repo).
