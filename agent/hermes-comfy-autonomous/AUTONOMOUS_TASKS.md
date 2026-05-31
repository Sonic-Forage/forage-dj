# Current Autonomous / Swarm Tasks

This file is the living task board for agents (Hermes or otherwise) working in this workspace.

## High Priority (Main Branch)

See `sessions/main-comfy-autonomous/session.json` in the project root for the full manifest.

Key standing tasks:
- Make ComfyUI the default, clean generation path in the CLI and core code.
- Improve general workflow execution (the new `run_comfy_workflow` helper is a start).
- Make remote ComfyUI servers (especially pods) easy and reliable to use.
- Evolve the `forage-comfy` skill into the agent's primary music generation interface.
- Build background/autonomous generation capabilities.
- Keep the terminal radio experience delightful and connected to new generations.

## Preservation Work (Legacy Branch)

See `sessions/legacy-stable-audio/session.json`.

Focus on:
- Not losing the old Stable Audio work.
- Creating good migration docs from the old Python backend to ComfyUI.
- Keeping that branch in a usable state for anyone who wants it.

## Experimental Work (Beta Branch)

See `sessions/beta-experimental/session.json`.

This is the place for:
- Crazy multi-workflow composition ideas
- Wild autonomous behaviors
- Early experiments with new models or ComfyUI features
- Experimental radio / interface ideas

## How to Pick Up Work

1. Read this file + `CURRENT_DIRECTION.md` + `BRANCH_STRATEGY.md`.
2. Look at the corresponding `sessions/xxx/session.json`.
3. Create or update tasks as you work.
4. When you finish something meaningful, update the relevant session and this file.

## Communication Rule for Agents

When working autonomously, always clearly state in any output or commit which branch you are targeting and which autonomous session you're advancing.

---

This workspace exists so that the user can walk away and a capable agent (Hermes or future systems) can continue making meaningful progress on the ComfyUI-powered autonomous DJ vision.
