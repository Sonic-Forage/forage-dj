# 🧠 AGENT START HERE - ForageDJ Autonomous Build System

**Welcome, autonomous builder.**

This folder contains everything you need to build, test, and iterate on ForageDJ **completely autonomously**.

---

## 🚀 MISSION

Build a working MVP of ForageDJ:
- Prompt-to-track generation using Stable Audio 3 (small models)
- 2-deck real-time mixer with EQ, filter, crossfader
- Seed-controlled setlist generation (One Prompt List → Infinite Unique Sets)
- Basic GUI (Dear PyGui or Gradio prototype)
- Run and test on a potato machine (CPU-only)
- Push working code back to main branch

**Goal**: A runnable `uv run foragedj` that lets a user type a prompt, generate a track, and mix it live.

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