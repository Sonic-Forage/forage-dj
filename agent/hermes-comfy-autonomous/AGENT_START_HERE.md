# AGENT START HERE — Hermes ComfyUI Autonomous Workspace

**Mission**: Turn ForageDJ into a high-quality, autonomous music generation system powered by **ComfyUI** (starting with ACE-Step 1.5 XL Turbo), supporting both local and remote servers. The user wants to generate music in the background while coding or vibing.

This folder is designed to be self-contained so a Hermes agent (or any capable agent) can pick it up and work autonomously, even remotely.

---

## Current Strategic Direction (2026-05-31)

We are making a hard pivot:

- **Primary Engine**: ComfyUI + strong audio workflows (especially ACE-Step 1.5 XL Turbo using `acestep-v1.5-xl-turbo`).
- **Why ComfyUI?** Much higher quality than the Python Stable Audio 3 models. Extremely flexible — you can drop in almost any workflow. Supports remote execution easily.
- **Stable Audio Python backend**: Quality was not good enough. All related code, experiments, and the old `generate_track` Python path have been moved to the `legacy/stable-audio` branch. Do **not** continue development on the Python Stable Audio path on `main` or `beta`.

**Branch Strategy (do not deviate without discussion)**:
- `main` → Clean, production-focused ComfyUI work.
- `legacy/stable-audio` → Frozen snapshot of all old Stable Audio work (preserved for history / people who still want it).
- `beta` → Experimental features (can be wild here).

---

## What We Are Moving Towards

1. **ComfyUI as the single high-quality generation backend** (local machine via Tailscale **or** remote GPU pods).
2. **Autonomous / background music generation** — the system can keep making tracks while the user is working on other things.
3. **"Vibe coding" radio** — terminal or web radio that plays freshly generated music in the background.
4. Easy workflow swapping — the user should be able to bring new ComfyUI workflows (especially audio ones) and have the system use them quickly.
5. Remote-first thinking — the user may be working from a different machine than where ComfyUI is running.

---

## Key Assets in This Workspace

- `PLANS/` — Current plans and architecture decisions.
- `KEY_WORKFLOWS/` — Important ComfyUI API workflows (start with the user's ACE-Step 1.5 XL Turbo workflow).
- `PROMPTS/` — Useful prompts for the agent (generation, debugging, architecture, etc.).
- `BRANCH_STRATEGY.md` — Detailed explanation of the three-branch model.
- `WHAT_WORKED.md` & `WHAT_DIDNT_WORK.md` — Institutional memory.
- `REMOTE_COMFYUI.md` — How to connect to remote vs local ComfyUI servers.
- `AUTONOMOUS_TASKS.md` — Current open autonomous work packages (linked to `sessions/` in the project).

---

## How to Work in This Environment

When a Hermes (or other) agent is pointed at this folder:

1. **Read `AGENT_START_HERE.md` first** (this file).
2. Read `BRANCH_STRATEGY.md` and `CURRENT_DIRECTION.md`.
3. Check the latest state of the three branches.
4. Look at open tasks in `AUTONOMOUS_TASKS.md` or the `sessions/` folder in the project root.
5. Prefer working on `main` unless the task is explicitly marked experimental.
6. When making changes, be extremely clear about which branch the work belongs on.
7. For any new ComfyUI workflow the user brings, add it to `KEY_WORKFLOWS/` with notes on how to drive it via the API.

---

## Important Principles

- **Quality over everything** — We moved away from Stable Audio Python because the quality wasn't there. Only accept ComfyUI workflows that sound significantly better.
- **Remote is first-class** — Assume the ComfyUI server might be on a different machine (RunPod, Vast, another computer, etc.).
- **Workflow flexibility** — The power of this direction is that the user can bring almost any good ComfyUI audio workflow. The system should make that easy.
- **Background generation** — One of the killer features is the ability to keep generating while the user is doing other work. Prioritize patterns that support this.
- **Preserve history** — Never delete the legacy branch work. It's valuable.

---

## Next Actions (for any agent picking this up)

See `AUTONOMOUS_TASKS.md` for the current prioritized list.

High-level standing goals:
- Make it trivial and reliable to generate high-quality music via ComfyUI from the `foragedj` CLI or scripts.
- Support easy switching between different ComfyUI servers.
- Build delightful "background radio" experiences (terminal + eventually web).
- Keep the agent workspace here self-documenting so future remote Hermes instances can continue without the full conversation history.

---

**You are now in the ComfyUI-first autonomous music era of ForageDJ.**

Welcome. Let's make something that sounds incredible and runs while the user is living their life.
