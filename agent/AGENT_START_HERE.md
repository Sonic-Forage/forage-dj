# 🧠 AGENT START HERE - ForageDJ Autonomous Build System

**Welcome, autonomous builder.**

This folder now points to specialized workspaces for different lines of work.

---

## Current Primary Focus

**ComfyUI-first autonomous music generation** (especially ACE-Step 1.5 XL Turbo).

See the dedicated workspace:

**`agent/hermes-comfy-autonomous/`**

This is the main folder a Hermes (or other capable remote) agent should use when working on the current direction.

It contains:
- Full context on the pivot away from Stable Audio Python
- Branch strategy
- What worked / what didn't
- Current plans
- Key workflows
- How to work with remote or local ComfyUI servers
- Open autonomous tasks

---

## Other Lines of Work

- `legacy/stable-audio` branch → All old Stable Audio Python work (preserved)
- `beta` branch → Experimental / high-risk ideas
- The old content that used to be in this file has been superseded by the focused workspace above.

---

## 📂 REPO STATE (Phase 0 Complete — Environment Ready)

- ✅ Working `uv sync` (fixed pyproject.toml, torch CPU indexes, removed non-existent stable-audio-3 pypi dep, proper extras/groups)
- ✅ Full module scaffolding + rich CLI (`foragedj doctor`, generate, gui, mix, midi-learn)
- ✅ scripts/setup.sh (one-shot bootstrap for humans + agents)
- Full whitepaper + research + architecture + agentic plan in `docs/`
- 4 open swarm issues for Phase 1 still active (claim them!)
- LICENSE, .python-version, improved .gitignore, tests/ skeleton in place
- Core imports now succeed after base `uv sync --extra gui --group dev`

Perfect handoff point for swarm agents.

---

## 📋 YOUR AUTONOMOUS WORKFLOW

1. **Read everything** in this folder and `docs/`
2. **Claim or create** the next task in GitHub Issues
3. **Build incrementally** (one feature at a time)
4. **Test on CPU** (potato machine mode)
5. **Commit + push** working code
6. **Update this file** with progress
7. **Repeat** until MVP is runnable

---

## 🔧 KEY FILES FOR YOU

- `agent/BUILD_WORKFLOW.md` — Step-by-step autonomous build plan
- `agent/TESTING_GUIDE.md` — How to test everything locally
- `agent/PROMPTS/` — Ready-to-use prompts for generation, debugging, and feature implementation
- `docs/AGENTIC_BUILD_PLAN.md` — Original 5-phase master plan
- `docs/AGENTIC_GENERATION_RELIABILITY_PLAN.md` — Critical: Current state + multi-track plan for making Stable Audio 3 "medium" (and reliable alternatives) actually work end-to-end from the local Z: checkpoint. Read this before touching audio_gen.py or generation.
- `docs/ARCHITECTURE.md` — Technical architecture
- `docs/FEATURES_SPEC.md` — Detailed feature list

---

## 🎯 SUCCESS CRITERIA (MVP v0.1 — Phase 0 Done, Phase 1 Active)

- [x] `uv sync` completes cleanly + `uv run foragedj doctor` passes core checks
- [x] Full module scaffolding + rich CLI with subcommands (`generate`, `doctor`, `gui`, etc.)
- [ ] User can enter a prompt + seed and generate a real 30–60s track (Phase 1 swarm)
- [ ] Two tracks loaded + mixed live with EQ/filter/crossfader (Phase 1)
- [ ] NS7II MIDI + voice (Phase 2)
- [ ] Code runs great on CPU-only potato machines
- [ ] Swarm agents delivering PRs against the 4 GitHub issues

---

**You are now in full autonomous mode.**

Start by reading `agent/BUILD_WORKFLOW.md` and begin Phase 1.

**Let's forge.** 🍓🎛️

*Part of the Sonic Forage mycelium*