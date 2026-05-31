# Plan: ComfyUI-First Autonomous Music Generation for ForageDJ (ACE-Step + Remote ComfyUI)

**Note**: This is a new/updated plan reflecting the user's decision to go all-in on ComfyUI + ACE-Step and deprecate the Stable Audio Python backend (see Context section below). Previous `forage-comfy` skill work is retained as useful foundation.

## Context & Motivation
The user has decided that the Python-based Stable Audio 3 models (small-music, small-sfx, medium, open) do not deliver sufficient quality for the project's needs. 

They want to:
- **Drop the Stable Audio Python backend** from active development on the main branch.
- Move all Stable Audio / stable-audio-3 related code to a separate branch (so it remains available if needed later).
- Go **all-in on ComfyUI**, specifically using high-quality workflows like their **ACE-Step 1.5 XL Turbo** workflow (using the `acestep-v1.5-xl-turbo` model).
- Use **ComfyUI as the primary (and eventually sole) music generation engine** for ForageDJ.
- Support both **local** (e.g. Windows machine via Tailscale) and **remote** (RunPod, Vast.ai, or other pods) ComfyUI servers.
- Build toward an **autonomous / background DJ** that can generate music while the user codes, vibes, or works — "make music to vibe code you and stuff".

The existing work on the `forage-comfy` skill, `comfy_client.py`, config system, and terminal radio is useful foundation material that can be adapted rather than discarded.

## Strategic Goals
1. Make high-quality ComfyUI generation (starting with ACE-Step 1.5 XL Turbo) the default and recommended path.
2. Provide excellent support for running ComfyUI remotely (pods) or locally.
3. Enable seamless "background radio" / autonomous generation experiences.
4. Keep the project usable as both a tool for the user and an autonomous music system.
5. Preserve the old Stable Audio Python backend on a branch for historical/reference purposes.
6. Evolve the `forage-comfy` skill into a powerful agent interface for ComfyUI-driven music work.

## Recommended Approach
**Pivot to ComfyUI as the core generation layer**, while keeping the project structure clean and the existing radio/player experiences intact.

**Major workstreams**:
- **Deprecation & Branching**: Remove or heavily deprecate the Python Stable Audio backend from `main`. Document the branch clearly.
- **ComfyUI Client Strengthening**: Adapt and extend `comfy_client.py` (or introduce a more general runner) to handle real-world audio workflows like the user's ACE-Step one.
- **Flexible Server Configuration**: Make it trivial to point the system at any ComfyUI server (local Tailscale, remote pod, etc.).
- **Skill Evolution**: Significantly expand `forage-comfy` so the agent excels at remote/local ComfyUI management, complex audio workflows, and background generation.
- **Autonomous Features + Radio**: Build background generation and polish the terminal radio as a first-class music consumption experience while coding.
- **Docs & Migration**: Clear branch strategy messaging.
**Evolve the existing `forage-comfy` skill** (do not create a completely new one unless name conflict) into a comprehensive, Hermes-inspired skill tailored to this exact environment and audio use case.

**Structure (inspired directly by Hermes creative-comfyui):**
- `SKILL.md` — High-quality, actionable agent prompt following the proven format (metadata, What's in this skill, When to Use, Architecture, Core Workflow / Decision Tree, Setup/Access notes specific to this machine, Pitfalls, Verification).
- `references/` folder (key docs the agent can load):
  - `tailscale-wsl-access.md` (current working setup, IPs, gotchas).
  - `c0mfy-install-layout.md` (blueprints/, custom_nodes of interest, models relevant to audio, how to access from WSL).
  - `audio-workflow-patterns.md` (Stable Audio 3 nodes, ACE-Step, differences between title-injection vs proper inputs, how to map project needs to blueprints).
  - `existing-client-integration.md` (how `comfy_client.py` + `generate_via_comfy` fits in; when to use the simple path vs general execution).
  - `blueprint-catalog.md` (auto-generated or curated list of useful audio blueprints from the install, with controllable params).
- `scripts/` folder (practical helpers the agent can execute):
  - `health_check_c0mfy.py` — Verifies Tailscale reachability to 100.99.10.17:8188, server stats, presence of key audio nodes (JK-AceStep, StableAudio*, etc.), basic smoke test with a known blueprint.
  - `list_blueprints.py` or `discover_audio_workflows.py` — Scan `/mnt/z/C0MFY/ComfyUI/blueprints/` for audio ones, extract high-level schema (using patterns from Hermes `extract_schema.py`).
  - `run_blueprint.py` (or extend/generalize the existing client) — Support general param injection for complex blueprints (not just hardcoded titles), output handling for audio, support for the project's output dir logic.
  - `sync_blueprint_to_project.py` — Helper to copy/adapt a useful blueprint from the main install into `workflows/comfy/` (with title nodes added for backward compat with current client if needed).
  - `check_audio_deps.py` — Given a blueprint or workflow, report missing custom nodes/models in the running server.
- Update existing ForageDJ files lightly if needed for better integration (e.g., improve `comfy_client.py` to support general workflows, or add COMFY_C0MFY_URL / install path awareness).
- Keep tight integration with ForageDJ's `COMFYUI_URL` env var and existing generation path.
- Make the skill "audio/DJ first" while still allowing general creative use of the C0MFY install.

**Access model:**
- Primary: HTTP API over Tailscale (the only reliable path from WSL agent).
- Supplemental: Direct filesystem reads of blueprints/custom_nodes (via the Z: mount) for discovery, schema extraction, and review. Never assume the agent can run `comfy` CLI commands directly (those run on the Windows host).

**Name / Invocation:**
- Keep/enhance as `forage-comfy` (or propose `forage-comfy-pro` / `c0mfy-audio` if clearer). Update description and trigger phrases heavily.
- Slash command `/forage-comfy`.

**Why this over alternatives:**
- Reusing the Hermes structure gives battle-tested organization, decision trees, and helper patterns without reinventing.
- Directly leverages the user's actual high-value asset (the C0MFY install + blueprints) instead of the minimal project workflows.
- Bridges the gap between "quick ForageDJ generation" and "full power of the creative workstation".
- Keeps changes focused on the skill + minimal supporting code in the project.

## Critical Files & Locations
- **New/Primary skill location**: `/mnt/z/IMF2045/forage-dj/.grok/skills/forage-comfy/` (expand with references/ and scripts/)
- Project Comfy integration (reuse heavily):
  - `src/foragedj/comfy_client.py` (core execution + output finding logic; will likely need generalization)
  - `src/foragedj/audio_gen.py` (backend dispatch)
  - `src/foragedj/paths.py` (get_comfy_workflows_dir, get_comfy_output_dir — extend for C0MFY awareness?)
  - `workflows/comfy/` + `workflows/comfy/README.md`
  - `docs/COMFYUI_SETUP.md`
  - `docker/docker-compose.yml` (the project's own Comfy profile for reference)
- User's main install (read-only discovery + reference in skill):
  - `/mnt/z/C0MFY/ComfyUI/blueprints/` (especially the three audio ones)
  - `/mnt/z/C0MFY/ComfyUI/custom_nodes/` (JK-AceStep-Nodes and any Stable Audio packs)
  - `/mnt/z/C0MFY/ComfyUI/models/`
- Hermes reference (for structure and script patterns):
  - The full content fetched from https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/creative/creative-comfyui (especially sections on architecture, core workflow, scripts like extract_schema/run_workflow/health_check, references/ contents, decision tree, pitfalls).
- Existing skill scaffolding: `/home/mindbots/.grok/skills/create-skill/SKILL.md` (for how to properly format the final SKILL.md).

## Existing Code & Patterns to Reuse
- `comfy_client.py`: `_resolve_comfy_url`, output directory search logic (`_get_possible_output_dirs`, `_find_output_file`), HTTP /prompt + /history polling, title-based injection, `test_comfy_connection`. Extend rather than replace.
- `paths.py`: `get_comfy_workflows_dir()`, `get_comfy_output_dir()`, `ensure_data_dirs()`.
- Hermes patterns (adapt, don't copy verbatim):
  - Two-layer architecture (lifecycle vs execution).
  - `extract_schema.py` style param discovery.
  - `run_workflow.py` style general execution with args dict.
  - `health_check.py` and verification checklist.
  - Decision tree + "when to use" sections.
  - references/ for deep docs the agent loads on demand.
- Project's current audio workflows and the title-injection convention (preserve for backward compat with `foragedj generate --backend comfy`).
- Tailscale reality (hardcoded known-good 100.99.10.17 + WSL IP 100.79.211.103 from conversation).

## Implementation Outline (High Level)
1. **Research/Review Phase** (this plan is part of it): Deep read of the three audio blueprints, key custom nodes, Hermes skill structure.
2. Design the exact `references/` and `scripts/` contents.
3. Write an upgraded `SKILL.md` following Hermes style + tailored content.
4. Implement 3–5 focused scripts (start with health_check + blueprint discovery + a generalized runner that can call the existing client or do direct API calls).
5. Update `comfy_client.py` (or add a new `c0mfy_runner.py` in the project) for better general support if the simple title path is insufficient for the rich blueprints.
6. Update project docs (`COMFYUI_SETUP.md`, `workflows/comfy/README.md`) to reference the new skill.
7. Add any needed .grok config or shell helpers for persistent `COMFY_C0MFY_URL` or install path.
8. Review step: Use the new skill + the Hermes reference to self-review the created skill for completeness (coverage of setup, execution, discovery, Tailscale, audio specifics, integration with ForageDJ, pitfalls).

## Verification Section
- The skill can be invoked and correctly describes the C0MFY install + Tailscale access.
- Agent using the skill can:
  - Successfully run `health_check` equivalent and confirm the RTX 4070 server + key audio nodes are present.
  - List and describe the audio blueprints.
  - Execute (or guide execution of) one of the Stable Audio 3 / ACE-Step blueprints with prompt/duration/seed injection, returning a usable audio file in the project's output dir.
  - Explain when to use the simple `generate_via_comfy` path vs full blueprint access.
- End-to-end test: From a fresh agent session, use `/forage-comfy` (or natural language trigger) to generate a short track using one of the advanced blueprints from the main install, with correct output handling.
- The skill documentation itself passes a "review with the Hermes creative-comfyui reference" — i.e., it has comparable depth in the relevant areas (references, scripts/helpers, decision trees, pitfalls specific to this WSL+Tailscale+audio setup).
- No breakage to existing `foragedj generate --backend comfy` flow using the small project workflows.

## Branch Strategy (Launched)
- `main` → Primary development line. ComfyUI + ACE-Step (and future strong ComfyUI audio workflows) as the core. Remote server support and autonomous generation are first-class.
- `legacy/stable-audio` → Complete snapshot of all previous Stable Audio Python backend work + related experiments. Preserved so nothing is lost. People who still prefer or need the old Python path can use this branch.
- `beta` → Experimental / high-risk / wild ideas. Can be branched from main. Things that are too unstable or exploratory live here until they prove themselves.

Autonomous work packages have been created in `sessions/`:
- `sessions/legacy-stable-audio/`
- `sessions/main-comfy-autonomous/`
- `sessions/beta-experimental/`

These can be picked up by swarm runs (`scripts/swarm_distributor.py` or future autonomous agents).

## Open Questions / Trade-offs (to resolve with user if needed)
- How aggressively do we want to delete vs just deprecate Stable Audio code on main?
- Do we want named server profiles (`local`, `runpod-pod-1`, etc.) or keep config simple for now?
- Priority order for the three autonomous sessions?

## Additional Details from Exploration (for implementer)
- Key audio blueprints to prioritize in the skill:
  - `/mnt/z/C0MFY/ComfyUI/blueprints/Audio Generation (Stable Audio 3 Medium).json`
  - `/mnt/z/C0MFY/ComfyUI/blueprints/Audio Generation (Stable Audio 3 Medium Base).json`
  - `/mnt/z/C0MFY/ComfyUI/blueprints/Text to Audio (ACE-Step 1.5).json`
- These use proper widget inputs (user_input / prompt, duration, seed) rather than relying solely on node "title" — the current `comfy_client.py` title injection will need extension or a parallel general execution path.
- Custom node of note: `JK-AceStep-Nodes` (and likely others under custom_nodes for Stable Audio 3).
- The main install has a very large `models/` and `custom_nodes/` (2869 entries) — the skill's health check and dep checker should be selective (focus on audio-relevant packs + Stable Audio checkpoints the user cares about for ForageDJ).
- Project's current `stable-audio-open.json` is a minimal StableAudioOpen_Conditioning + Sampler + SaveAudio example using widget_values + title nodes. It must continue to work.
- Output from the C0MFY server currently lands in its own `output/` dir on Windows; the skill (and any improved runner) must route or copy useful audio back into the project's `comfyui_output/` or `generated/` using the existing `_find_output_file` / paths logic.
- The Hermes skill's `run_workflow.py` + `extract_schema.py` patterns are the gold standard to emulate for the new general execution helpers.

## Key Technical Considerations
- **Remote vs Local ComfyUI**: The client and tooling must work cleanly whether the server is local (Tailscale) or on a remote GPU pod. Output routing and file discovery need to be flexible.
- **Complex Workflows**: The user's ACE-Step workflow uses internal nodes for prompt engineering. Simple title-based injection is insufficient long-term; we need better general parameter injection.
- **Background Generation**: Support fire-and-forget or queued generations so the user can keep working ("vibe coding").
- **Asset Split**: Heavy models live on the ComfyUI server side. ForageDJ mainly needs good workflow execution + output handling.

## Implementation Outline (Pragmatic Phases)
1. **Direction & Cleanup** — Create legacy branch for Stable Audio Python code. On main, make "comfy" the clear default in `audio_gen.py`, CLI, and docs.
2. **Client & Config** — Strengthen `comfy_client.py` / config for general audio workflows and easy remote server switching.
3. **Skill Evolution** — Update and expand `forage-comfy` (SKILL.md, references, scripts) to be the agent's primary interface for ComfyUI music work, including remote pods and background use.
4. **Autonomous + Radio Polish** — Improve background generation support and the terminal radio experience so it feels like a live station fed by ComfyUI.
5. **Docs & Polish** — Clear migration docs, updated setup guides, and verification that the old Python path is properly off main.

## Verification
- `foragedj generate` (no `--backend`) reliably uses ComfyUI and produces high-quality results via ACE-Step-style workflows.
- Easy to point the system at different ComfyUI servers (local Tailscale vs remote pod).
- The `forage-comfy` skill is actively useful for the agent in generation, remote setup, and autonomous scenarios.
- The terminal radio consumes newly generated ComfyUI tracks smoothly.
- Stable Audio Python code is cleanly on a documented branch, not cluttering main.

This direction directly matches the user's current vision: high-quality autonomous music via ComfyUI (local or remote), with the ability to generate while coding or vibing. Previous skill and config work is directly reusable and can be accelerated.
