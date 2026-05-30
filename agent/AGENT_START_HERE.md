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

## 📂 REPO STATE (as of now)

- README cleaned (logo removed temporarily)
- Full whitepaper + research in `docs/`
- Architecture, features spec, hardware notes ready
- 4 open swarm issues for Phase 1
- pyproject.toml with all dependencies
- No core code written yet (perfect starting point)

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

## 🎯 SUCCESS CRITERIA (MVP v0.1)

- [ ] `uv sync` completes without errors
- [ ] `uv run foragedj` launches a simple interface
- [ ] User can enter a prompt + seed and generate a 30–60s track
- [ ] Two tracks can be loaded and mixed live (volume + crossfader)
- [ ] Basic EQ/filter works in real time
- [ ] Code runs on CPU-only machine
- [ ] All changes committed and pushed

---

**You are now in full autonomous mode.**

Start by reading `agent/BUILD_WORKFLOW.md` and begin Phase 1.

**Let's forge.** 🍓🎛️

*Part of the Sonic Forage mycelium*