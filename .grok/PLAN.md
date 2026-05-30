# Forage-DJ: Model Pre-Download, Setlist Manifests & Engine Test Harness (Offline Potato Ready)

**Session**: 019e79f2-017b-77d2-8a8d-5859e69f240f (continued / new phase)  
**Date**: 2026 (context)  
**Status**: Fresh plan — ready for approval via `exit_plan_mode`

**Note**: This is a new focused planning session. Previous Phase 0 (env + scaffolding + initial swarm agents for audio_gen + mixer/GUI) is complete and archived in `.grok/PLAN.md` (project root copy) and `.grok/swarm-outputs/`. This plan builds directly on that foundation.

---

## 1. Context & Current State Evaluation

**User Request (new phase)**: 
- Pre-download all relevant Stable Audio 3 models (small-music, small-sfx, medium + optimized variants + SAME autoencoders) into a dedicated `checkpoints/` folder in the project root on the large Z: drive (`/mnt/z/IMF2045/forage-dj`).
- Control Hugging Face cache to live on Z: (not default home/C: cache) for space reasons.
- Investigate and use ONNX where possible from the stable-audio-3 repo (optimized/ folder contains TensorRT/MLX — limited native ONNX; note findings).
- Create reproducible "setlist manifests" (locked seeds) for a "Bass House Jamz / House music" theme, using the official prompting guide.
- Do **not** generate audio yet — just prepare the manifests as ready-to-process "scores".
- Create two variants (different seeds) with good naming.
- Add proper tests for the generation engine.
- Test output folder.
- Launch a swarm (including headless mode) to test the engine once assets are local.
- Goal: Full offline "potato machine" testing capability.

**Evaluation against previous plan**:
- Previous plan (environment hygiene + scaffolding + first two swarm agents) is **largely executed**.
- Current code has working (guarded) `audio_gen.py` (from first swarm agent), enhanced `mixer.py` + minimal launchable `gui.py` (from second agent).
- No `checkpoints/` folder exists yet.
- No manifests, no dedicated model pre-download script, no engine tests beyond basic, HF cache not pinned to Z:.
- This is a **distinct new phase** focused on **assets + reproducibility + testing harness**.

**Why now?** User wants to move from "code compiles/runs" to "we can actually test real generation offline on potato hardware with reproducible setlists".

**Project root discipline** (per latest user instruction): Everything (checkpoints, cache hints, manifests, test outputs, swarm artifacts) must live under `/mnt/z/IMF2045/forage-dj`.

---

## 2. Recommended Approach

**Core Objective**: Make the generation engine fully testable offline on a potato machine by pre-caching **all** required model weights on the large Z: drive, creating locked-seed setlist manifests as the "compositional score", adding real tests + a headless test runner, and launching a parallel swarm to validate everything.

**Design Principles**:
- **Offline-first / potato friendly** — after one-time download on a machine with bandwidth, everything runs locally with no network.
- **Reproducible by design** — locked seeds + manifest files = shareable "setlist recipes".
- **Z: drive native** — all large artifacts (checkpoints + HF cache) live under the project on the spacious drive.
- **Manifest over hard-coded** — setlists are data (YAML/JSON), not code.
- **Swarm + headless** — agents can run test batches without GUI.
- **Safety/culture preserved** — every manifest and generated output carries the harm-reduction note.

**Key Technical Decisions**:
- **Download method**: Use `huggingface_hub.snapshot_download(..., local_dir=...)` + `local_files_only=True` later in `audio_gen.py`. Script sets `HF_HOME` / `HUGGINGFACE_HUB_CACHE` to a Z:-based path (e.g. `/mnt/z/IMF2045/forage-dj/.cache/huggingface`).
- **ONNX investigation**: Check the stable-audio-3 `optimized/` folder + repo for any ONNX export/inference path (current research: primarily TensorRT and MLX; no first-class ONNX yet). If none, document and keep PyTorch path as primary. Provide optional future hook.
- **Checkpoints layout**:
  ```
  checkpoints/
    stable-audio-3-small-music/
    stable-audio-3-small-sfx/
    stable-audio-3-medium/
    stable-audio-3-optimized/   (if useful files)
    SAME-S/
    SAME-L/
  ```
- **Manifest format** (simple, versioned):
  ```yaml
  name: "Bassline Dominion - House Ignition"
  seed: 424242          # locked
  version: 1
  theme: "Bass House / UKG / 4x4 energy"
  prompts:
    - prompt: "..."
      duration: 60
      model: "small-music"
    ...
  ```
- **Two manifests**:
  1. Primary with "good" seed (e.g. 424242).
  2. Completely different seed variant (e.g. 777777 or 20260613).
- **Naming**: Fun but professional — e.g. "Forage House: Bassline Dominion (Locked Seed 424242)".
- **Testing**:
  - Pytest for manifest loading/validation.
  - Dry-run engine tests (mock the model).
  - Headless CLI: `uv run foragedj test-setlist --manifest setlists/bass-house-001.yaml --output-dir test_outputs/ --headless --limit 2`.
- **Swarm launch**: 3–4 parallel agents for download script + cache pinning, manifest creation + prompting guide application, test harness + headless runner, potato compatibility verification.

**Risks & Mitigations**:
- Very large downloads (several GB): Do on a machine with good bandwidth + space on Z:. Script is resumable via HF hub.
- ONNX not ready: Document honestly; focus on PyTorch small models for potato CPU path.
- Cache on Z: in container vs host: Provide clear env var + docker notes if needed.
- Space: User confirmed Z: has room; we'll put both `checkpoints/` and `.cache/huggingface` under the project tree.

---

## 3. Files to Create / Modify (Exact List)

### Create
- `checkpoints/` (directory — add `.gitkeep` + update `.gitignore` to allow the dir but perhaps large files via git-lfs or explicit ignore for safetensors/bin in future).
- `scripts/download_checkpoints.py` (or .sh) — main downloader with HF cache control + progress.
- `setlists/` directory
  - `bass_house_ignition_seed424242.yaml` (primary "Bass House Jamz" manifest)
  - `bass_house_ignition_seed777777.yaml` (different seed variant)
- `tests/test_generation_engine.py` (manifest parsing, dry generation, provenance checks).
- `test_outputs/` (directory for headless test runs — gitignored).
- `.grok/swarm-outputs/` (already partially exists — add new agent reports here).
- Possibly `docs/GENERATION_TESTING.md`.

### Modify
- `src/foragedj/audio_gen.py` — add optional `checkpoint_dir` param or env var support so it can load from local `checkpoints/` with `local_files_only`.
- `src/foragedj/cli.py` — new subcommands: `download-models`, `test-setlist`, `list-manifests`.
- `.gitignore` — ensure `test_outputs/`, `checkpoints/*.safetensors` (or selective), `.cache/` patterns are handled nicely.
- `scripts/setup.sh` — optional hook to call the downloader or remind about it.
- `docs/SWARM_STATUS.md` + `GROK_SESSION.md` — record this phase.
- `README.md` — quick note on "Pre-downloaded models for offline use".

**Reusable existing code**:
- Current `audio_gen.py` structure + `utils.embed_metadata` + `SAFETY_NOTE`.
- Prompting best practices from the linked stable-audio-3 `docs/guides/prompting.md`.
- Existing swarm output format in `.grok/swarm-outputs/`.
- `foragedj doctor` pattern for new health checks.

---

## 4. Detailed Execution Steps (for after approval)

1. **Cache & Directory Setup**
   - Create `checkpoints/` and project `.cache/huggingface/`.
   - Script that does `export HF_HOME=/mnt/z/IMF2045/forage-dj/.cache/huggingface` before any downloads.

2. **Model Downloads** (prioritized)
   - Main inference: small-music, small-sfx, medium.
   - Autoencoders: SAME-S, SAME-L (from extra collection).
   - Optimized variants if they contain useful weights/scripts.
   - Verify each lands in `checkpoints/<name>/`.

3. **ONNX Research + Decision**
   - Inspect stable-audio-3 `optimized/` + any export scripts.
   - If viable ONNX path exists for small models → implement thin loader.
   - Otherwise document "PyTorch primary for now; ONNX future".

4. **Setlist Manifests (House / Bass House theme)**
   - Study the prompting guide.
   - Craft 6–10 high-quality prompts in the Bass House / UK Bass / energetic house space.
   - Lock one seed for the whole manifest (e.g. 424242).
   - Create second manifest with completely different seed.
   - Nice name: "Forage House: Bassline Dominion — Locked Seed Edition".

5. **Engine Tests & Headless Harness**
   - Pytest suite that can run with or without real models (mocks when unavailable).
   - Headless test runner that processes a manifest, writes to `test_outputs/<manifest-name>-seedXXXX/`, records timing + provenance.
   - "Potato mode" flag that prefers small models + shorter durations.

6. **Swarm Launch (this phase)**
   - Agent A: Download script + cache pinning + ONNX research.
   - Agent B: Manifest creation (2 variants) + documentation.
   - Agent C: Test harness + CLI commands + pytest.
   - Agent D (optional): Headless swarm runner that executes a mini-manifest and reports results.

---

## 5. Verification & Success Criteria

**Must pass**:
- `checkpoints/` contains the requested models (or clear symlinks/snapshots).
- HF cache is writing to Z: drive location.
- Both manifests are valid YAML/JSON, load cleanly, have locked seeds, and follow prompting guide style.
- `uv run pytest tests/test_generation_engine.py` passes (including manifest tests).
- `uv run foragedj test-setlist --manifest setlists/bass_house_ignition_seed424242.yaml --headless --limit 1 --dry` works and produces expected metadata in `test_outputs/`.
- On a potato machine (after copy of checkpoints + cache), generation works fully offline.
- Swarm agents complete their tasks and leave reports in `.grok/swarm-outputs/`.
- `foragedj doctor` gains a "Models" section that reports local checkpoint status.

---

## 6. Swarm Prompts (Ready to Spawn)

After core download + manifest scripts land:

- "You are the Download & Cache agent. Implement scripts/download_checkpoints.py that respects Z: drive, downloads exactly the 6 repos the user listed, prefers any ONNX assets in the stable-audio-3 optimized folder, and updates audio_gen.py to support local loading."
- "You are the Manifest agent. Using the official prompting.md, create two beautiful Bass House themed setlist manifests with locked different seeds. Put them in setlists/. Add validation + nice CLI listing."
- "You are the Test Harness agent. Build pytest coverage for the generation path + a headless `test-setlist` command that can run manifests and write reproducible test outputs."

---

**This plan is self-contained, respects the master repo location on Z:, and directly delivers what the user asked for right now.**

**Next**: Review this plan. When ready, call `exit_plan_mode`. We will then execute the downloads, manifests, tests, and launch the targeted swarm — all with artifacts living cleanly under `/mnt/z/IMF2045/forage-dj`.

*Part of the Sonic Forage mycelium — ready to forge offline.* 🍓🎛️


---

## 1. Context & Full Folder Review Summary

**Project**: forage-dj (https://github.com/Sonic-Forage/forage-dj) — ambitious local-first AI DJ DAW using Stable Audio 3 (small models), prompt-as-setlist scores + seed variation, 2-4 deck real-time mixing, Numark NS7II MIDI, voice, autonomous Ralph-loop agent, stems. "One setlist + one seed = unique performance."

**Why this request?** User reports "having issues with what we have here" for `uv venv sync`. The repo cannot currently reach a working development environment, blocking all progress and the advertised "swarm active" collaboration.

**Complete inventory** (exhaustive via `find`, `list_dir`, `read_file`, `grep` across all 13 files; no other source/config/tests exist):
- Root: README.md, pyproject.toml, .gitignore (only)
- src/foragedj/: __init__.py (broken imports), cli.py (placeholder only)
- docs/: 6 excellent specs — AGENTIC_BUILD_PLAN.md (detailed 5-phase agent-executable), ARCHITECTURE.md (layered with exact module names/signatures), FEATURES_SPEC.md (P0-P3), WHITEPAPER.md (formal innovation + roadmap), RESEARCH_SUMMARY.md (Stable Audio 3 + Mixxx/NS7II refs), HARDWARE_NS7II.md (mapping + learn flow)
- agent/: AGENT_START_HERE.md, BUILD_WORKFLOW.md (step-by-step phases), TESTING_GUIDE.md (potato-machine checklist + commands)
- No: uv.lock, .python-version, LICENSE, tests/, scripts/, .github/, py.typed, pre-commit, ruff config, src subpackages (hardware/, gui/ etc.), no real implementation modules

**Key blocking issues for `uv sync`** (directly cause user pain):
1. **Non-existent PyPI dep**: `"stable-audio-3>=0.1"` — research confirms (web + GitHub) this package name does **not** exist on PyPI. The official library lives at https://github.com/Stability-AI/stable-audio-3 (import `stable_audio_3`). Install via `git clone && uv sync` inside that repo (or `pip install -e .`). Listing it here makes every sync fail.
2. **Invalid TOML syntax for extras**: `cpu = ["torch>=2.4.0 --index-url https://download.pytorch.org/whl/cpu"]` — `--index-url` is not valid inside a PEP 508 requirement string. uv/pip will reject.
3. **Heavy deps in core**: `demucs`, `faster-whisper`, `dearpygui` (plus transitive torch) bloat install time/RAM, cause conflicts on CPU-only "potato machines" (explicit target), and belong in later phases (P1+ per FEATURES_SPEC).
4. **Missing uv hygiene**: No `[[tool.uv.index]]` / sources for torch CPU wheels, no `dependency-groups`, no python pin. No lockfile committed.
5. **Runtime breakage**: `from . import audio_gen, mixer...` in __init__.py will explode on any `import foragedj` or `uv run`. CLI only prints text; no subcommands matching TESTING_GUIDE expectations (`generate`, `gui`, `mix`).
6. **.gitignore bug**: `~/.foragedj/` entry is invalid (tilde not expanded in gitignore; should be `.foragedj/` or absolute patterns).
7. **No setup automation**: Phase 0 in own AGENTIC_BUILD_PLAN explicitly calls for `scripts/setup.sh`, updated README, working `uv sync`.

**Current env (this workspace)**: Ubuntu 24.04, Python 3.12.3 (good), pip present, **uv absent from PATH**, no .venv, no uv.lock. Matches typical fresh clone pain.

**Positive assets** (leverage heavily):
- World-class docs written for exactly this (AI agents + swarm).
- Clear acceptance criteria per phase.
- Cultural DNA (Sonic Forage harm-reduction, safety gates, public-safe defaults) baked into every spec.
- GitHub swarm issues already referenced (#1-4 for Phase 1).
- MCP `grok_com_github` connected (can create comments, manage issues/PRs in execution).

**Git state**: Clean on main, up-to-date with origin. Perfect starting point for improvements + swarm.

This review used parallel exploration (list_dir + multiple read_file + grep + targeted web_search on stable-audio-3 install + run_terminal for hidden files + system facts). No modifications performed.

---

## 2. Recommended Approach (Chosen Path)

**Core objective**: Deliver a **working `uv sync` environment** (and `uv run foragedj`) in one pass so the user + swarm can immediately continue. Simultaneously "improve anything" in foundation (Phase 0 hygiene complete + scaffolding for Phase 1 per their own plans) and prepare/launch a parallel swarm.

**Design principles** (aligned with project values):
- Local-first, potato-machine friendly (CPU-only first).
- Modular & forkable (stubs with clear contracts from ARCHITECTURE + BUILD_PLAN).
- Agent-friendly (files + prompts ready for subagents).
- Pragmatic over purist: stable-audio-3 stays out of core pyproject to guarantee sync succeeds; documented opt-in path + runtime guards.
- Reproducible: commit uv.lock after first successful sync.
- Safety/culture: every new stub and doc update preserves harm-reduction notes + provenance.

**Key technical decisions & trade-offs** (why this over alternatives):
- **stable-audio-3 handling**: Git dep in pyproject rejected (torch version hell, Flash-Attn build pain, long clones on every sync, conflicts with the lib's own uv.lock). Alternative (clone + PYTHONPATH or editable in post-install) chosen. Matches official Stability docs exactly. Stubs will guide user precisely.
- **Torch CPU extras**: Proper `[[tool.uv.index]]` + `[tool.uv.sources]` mapping (modern uv 2026 pattern) instead of hacky strings or "just use pip". Fallback: setup.sh performs explicit torch CPU pre-install if index resolution is flaky on first try. Better than forcing `--index-url` on every command.
- **Dependency split**: Core = minimal real-time audio foundation (sounddevice + pedalboard + librosa + MIDI + numpy/scipy). Everything else (gen, gui, voice, stems) = optional extras + groups. Enables fast `uv sync` for CLI-only hacking; `uv sync --extra gui --extra gen` for full.
- **GUI choice**: Keep Dear PyGui (per ARCHITECTURE, FEATURES, BUILD_WORKFLOW). No switch to Gradio (would be easier web but violates "fast native on potato" + existing specs).
- **CLI framework**: Keep stdlib argparse initially (zero new deps). Upgrade path to typer/rich noted for Phase 1. Subcommands exactly match TESTING_GUIDE + AGENTIC_PLAN expectations.
- **Structure creation**: Create full module skeletons now (audio_gen.py, mixer.py, analysis.py, hardware/midi.py, gui.py stubs) matching exact function signatures in docs. Swarm agents inherit files instead of starting from blank slate — massive velocity win. Matches "Phase 0 + start Phase 1" in their plans.
- **Swarm launch**: Not just docs update. Use `spawn_subagent` (multiple in parallel, general-purpose + targeted prompts referencing this plan + AGENTIC_BUILD_PLAN.md) + todo_write for visibility + MCP GitHub tools to post status to the 4 open issues. Isolated worktrees optional for riskier audio modules. "Best-of-n" or review skill can be layered for critical pieces.
- **Scripts**: One powerful `scripts/setup.sh` (idempotent, detects OS, installs uv + system audio dev libs on Ubuntu/Debian, runs syncs, prints next steps). Directly fulfills AGENTIC_BUILD_PLAN Phase 0 task #4.
- **Lockfile**: Generate + commit `uv.lock` during validation (reproducibility for swarm contributors on identical CPUs).

**Out of scope for this plan** (defer to swarm):
- Full Stable Audio 3 wrapper impl (Phase 1 task).
- Real Dear PyGui 2-deck + waveform (biggest UI lift).
- MIDI hardware testing (needs NS7II or virtual).
- Any model downloads or real generation runs (network + disk heavy).

**Risks & mitigations**:
- Index resolution for torch CPU varies by uv version: setup.sh + doctor command will detect + offer fallback `uv pip install "torch>=2.4.0" --index-url https://...`.
- Linux audio build deps (PortAudio, ALSA, JACK): setup.sh handles apt; documents for Fedora/Arch/Mac/Windows.
- Dear PyGui + sounddevice wheels on Py 3.12 Ubuntu: reliable in 2026 but doctor will verify `import sounddevice`.
- Subagent coordination: Main thread owns todo list + aggregates results via `get_command_or_subagent_output`.

---

## 3. Files to Modify or Create (Exact List)

### Modify (8 files)
- [pyproject.toml](/mnt/z/IMF2045/forage-dj/pyproject.toml) — Major rewrite (see section 4)
- [README.md](/mnt/z/IMF2045/forage-dj/README.md) — Update Quick Start, Status, Prerequisites, add doctor command, link to new scripts/setup.sh
- [.gitignore](/mnt/z/IMF2045/forage-dj/.gitignore) — Fix `~/.foragedj/` → `.foragedj/`, add `uv.lock` (no, we will commit it), add `scripts/.local/`, `*.log`, HF cache hints
- [src/foragedj/__init__.py](/mnt/z/IMF2045/forage-dj/src/foragedj/__init__.py) — Remove broken imports; export version + lazy accessors + safety note
- [src/foragedj/cli.py](/mnt/z/IMF2045/forage-dj/src/foragedj/cli.py) — Full upgrade: subcommands (generate, gui, mix, midi-learn, doctor, version), pretty output, import guards
- [docs/AGENTIC_BUILD_PLAN.md](/mnt/z/IMF2045/forage-dj/docs/AGENTIC_BUILD_PLAN.md) — Mark Phase 0 complete, add "Environment fixed [date]. Swarm launched." note, update handoff
- [agent/AGENT_START_HERE.md](/mnt/z/IMF2045/forage-dj/agent/AGENT_START_HERE.md) — Update "REPO STATE", success criteria (all checked for env), add "Swarm now active — claim via GitHub"
- [agent/BUILD_WORKFLOW.md](/mnt/z/IMF2045/forage-dj/agent/BUILD_WORKFLOW.md) — Update Phase 0 status to done, add post-fix steps

### Create (14+ files)
**Config / Root**:
- `.python-version` (content: `3.12`)
- `LICENSE` (MIT, matching README claim)
- `uv.lock` (generated during validation run; committed)

**Scripts (fulfills Phase 0)**:
- `scripts/setup.sh` (executable, ~80 lines: uv bootstrap, apt audio libs, uv sync variants, stable-audio-3 clone helper, post-install doctor)
- `scripts/README.md` (usage + maintenance)

**Core Package Scaffolding (matches ARCHITECTURE + AGENTIC_BUILD_PLAN signatures exactly)**:
- `src/foragedj/audio_gen.py` (stub `generate_track(prompt: str, seed: int = 42, duration: float = 60.0, model: str = "small-music") -> Path`, clear error + install instructions, metadata embedder skeleton)
- `src/foragedj/mixer.py` (Deck dataclass + basic Mixer with sd + pedalboard stubs for volume/EQ/filter/crossfade)
- `src/foragedj/analysis.py` (librosa bpm/key/onset wrappers, Camelot helper stub)
- `src/foragedj/gui.py` (minimal dearpygui launcher stub or "install --extra gui" message)
- `src/foragedj/voice.py` (stub)
- `src/foragedj/agent.py` (stub, references sonic-forage-autonomous-dj-os)
- `src/foragedj/utils.py` (config, logging, metadata embedding helpers — safety note injector)
- `src/foragedj/hardware/__init__.py`
- `src/foragedj/hardware/midi.py` (NS7II mapping dict + learn stub using mido)
- `src/foragedj/hardware/osc.py` (placeholder)

**Testing / CI Foundation**:
- `tests/__init__.py`
- `tests/test_cli.py` (basic argparse + doctor tests)
- `tests/test_analysis.py` (librosa smoke if present)
- `.github/workflows/ci.yml` (minimal: lint + test + uv sync matrix on ubuntu/mac, optional later)

**Optional polish** (include if time):
- `ruff.toml` or `[tool.ruff]` in pyproject
- `.pre-commit-config.yaml` (ruff, pyright? )
- `docs/SWARM_STATUS.md` (living list of claimed tasks + agent names)

All new code will be minimal, import-safe, well-commented only where it aids swarm handoff, and runnable immediately after `uv sync`.

**Reusable existing code / patterns**:
- Current cli.py argparse structure (line 5-18)
- Exact function signatures and acceptance criteria from docs/AGENTIC_BUILD_PLAN.md:40-68 and docs/ARCHITECTURE.md:53-64
- Safety/harm-reduction language from WHITEPAPER.md and README
- Potato-machine targets from multiple docs

---

## 4. Concrete pyproject.toml Changes (Summary of New Content)

```toml
[project]
name = "forage-dj"
version = "0.1.0"
description = "..."
requires-python = ">=3.12"
license = {text = "MIT"}
dependencies = [
    "sounddevice>=0.4.6",
    "python-rtmixer>=0.1.0",
    "pedalboard>=0.9.0",
    "librosa>=0.10.0",
    "mido>=1.3.0",
    "python-rtmidi>=1.5.0",
    "numpy>=1.26.0",
    "scipy>=1.13.0",
    # NOTE: stable-audio-3, dearpygui, demucs, faster-whisper moved to extras
]

[project.optional-dependencies]
gui = ["dearpygui>=1.11.0"]
gen = []  # populated at runtime via instructions; see scripts/setup.sh
voice = ["faster-whisper>=1.0.0"]
stems = ["demucs>=4.0.0"]
full = ["forage-dj[gui,gen,voice,stems]"]  # meta

[project.scripts]
foragedj = "foragedj.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/foragedj"]

[tool.uv]
index-url = "https://pypi.org/simple"

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cpu" }
torchaudio = { index = "pytorch-cpu" }

[dependency-groups]
dev = ["ruff>=0.4", "pytest>=8.0", "pytest-asyncio", "mypy>=1.10"]
```

Plus updated README notes on `uv sync --extra gui --group dev` etc.

This guarantees clean sync while preserving full vision.

---

## 5. Swarm Launch Plan (Post-Fix Execution)

**Immediate after env validation succeeds**:

1. Update all "swarm active" badges/text + create `docs/SWARM_STATUS.md` (or use GitHub issues as source of truth).

2. Use `spawn_subagent` (4+ in one response for parallelism):
   - Subagent 1 (general-purpose): "Phase 1 Audio Gen + Seed Control — read plan.md + docs/AGENTIC... Implement stable-audio-3 wrapper in audio_gen.py using the stub. Support seed. Cache to ~/.foragedj/generated. Add safety metadata. Test CPU generate."
   - Subagent 2: "Phase 1 Mixer + 2-Deck GUI — implement mixer.py real-time engine + dearpygui_app.py (or gui.py) 2-deck panels per FEATURES_SPEC P0."
   - Subagent 3: "Phase 2 NS7II MIDI + Voice — hardware/midi.py full mapping + learn + voice.py STT/LLM intent (start with stubs + basic mido)."
   - Subagent 4: "Phase 3 Setlist Editor + Autonomous — setlist runner + integrate autonomous-dj-os Ralph loop (thin wrapper first)."
   - Optional 5th: "Testing + CI + docs polish swarm agent" (uses TESTING_GUIDE, adds real tests, updates whitepaper if needed).

3. All subagents instructed to:
   - Start with `uv sync` in their context
   - Use todo_write for their local tasks
   - Report status back
   - Respect Sonic Forage gates

4. Main orchestrator (this session): monitor via `get_command_or_subagent_output`, aggregate, use `grok_com_github` MCP tools (after `search_tool` schema) to comment on https://github.com/Sonic-Forage/forage-dj/issues/1 etc. with progress + PR links.

5. Optional: Use "implement" skill for one high-risk module, or "best-of-n" for critical audio latency choice.

**Swarm success metric**: At least 2 of the 4 Phase 1 issues move to "in review" or merged within one session cycle; `uv run foragedj gui` shows interactive (even mock) 2-deck demo.

---

## 6. Verification & Success Criteria (End-to-End)

**Must pass before declaring victory** (run in order):

1. **Bootstrap** (any machine):
   ```
   # one-time
   curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="$HOME/.local/bin:$PATH"
   cd forage-dj
   ```

2. **Setup script**:
   ```
   chmod +x scripts/setup.sh
   ./scripts/setup.sh --cpu   # or --full
   ```
   → Exits 0, prints "Environment ready. Next: uv run foragedj doctor"

3. **Core sync verification**:
   ```
   uv sync --extra gui --group dev
   uv run foragedj --version
   uv run foragedj doctor          # must pass all checks except "gen" (expected)
   uv run python -c "import foragedj; from foragedj import audio_gen, mixer; print('Imports OK')"
   ```

4. **Potato-machine checklist** (from TESTING_GUIDE):
   - Install time <5min on CPU-only
   - No OOM on 8GB
   - `uv run foragedj generate "test prompt" --seed 42 --dry` works (mock path)
   - GUI stub launches or gives actionable message

5. **Docs consistency**: Grep confirms every doc references the new `scripts/setup.sh` and current status.

6. **Swarm handoff**: `docs/SWARM_STATUS.md` exists, GitHub issues updated via MCP, 1+ subagent has produced a diff that passes `uv run pytest`.

7. **Lockfile**: `uv.lock` present, committed, `uv sync` is reproducible.

8. **No regressions**: `git status` clean except intentional new files + lock; all original docs content preserved/enhanced.

**Rollback**: Any step fails → `git checkout -- pyproject.toml src/foragedj/` + manual minimal toml documented in plan appendix.

---

## 7. Execution Notes for After Approval (exit_plan_mode)

- Use `todo_write` immediately with 8-10 items (env fix, each new file, validation, swarm spawn x4, doc updates, github sync, final review).
- Prefer search_replace for all edits (read first).
- For new files: search_replace with `old_string=""` works reliably for creation.
- Spawn subagents only after core env PR changes are solid (or in parallel worktrees if isolation needed via `isolation="worktree"`).
- Leverage MCP `grok_com_github`: first `search_tool` for "github" schema, then `use_tool` for issue comments.
- After swarm tasks complete one cycle: run full verification, update this plan.md with "Executed" notes, prepare handoff PR description.
- If uv index issues appear during validation: iterate 1-2 times with setup.sh tweaks (documented).

**This plan is self-contained, references every critical file/line pattern, and directly enables the user's request: working uv environment + improvements + swarm activation.**

---

**Next action**: Review this plan (use `read_file` on the path if needed). When satisfied, call `exit_plan_mode` (no text question about "is this okay?"). We will then execute with full power + parallel agents.

**Important for the user**: An editable copy of this plan lives in the master repo at:
- `/mnt/z/IMF2045/forage-dj/.grok/PLAN.md`
- Also linked from `/mnt/z/IMF2045/forage-dj/GROK_SESSION.md`

All future session state, swarm outputs, and notes will be organized under the project root (big drive) inside `.grok/`.

*Part of the Sonic Forage mycelium — ready to forge.* 🍓🎛️

---

## Appendix A: Linux System Packages (for setup.sh + manual)

Ubuntu/Debian (add to scripts/setup.sh):
```bash
sudo apt-get update
sudo apt-get install -y \
    libportaudio2 portaudio19-dev \
    libasound2-dev \
    libjack-jackd2-dev jackd2 \
    ffmpeg \
    libsndfile1 \
    build-essential \
    python3-dev
```

Fedora: `dnf install portaudio-devel alsa-lib-devel jack-audio-connection-kit-devel ffmpeg`

This prevents "PortAudio" or "sounddevice" build failures (common on fresh Linux for realtime audio).

---

## Appendix B: Example audio_gen.py Stub Skeleton (for immediate implementation)

```python
"""Audio generation stub — Phase 1 implementation target.

See docs/AGENTIC_BUILD_PLAN.md:40 and docs/ARCHITECTURE.md:55.
"""

from __future__ import annotations
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SAFETY_NOTE = "Public-safe rave tool — harm reduction first. Prompt provenance embedded."

def generate_track(
    prompt: str,
    seed: int = 42,
    duration: float = 60.0,
    model: str = "small-music",
    progress_callback: Optional[callable] = None,
) -> Path:
    """Generate audio from prompt + seed. Returns path to WAV.
    
    MVP target: <30s for 60s track on CPU (small model).
    """
    try:
        from stable_audio_3 import StableAudioModel  # type: ignore
    except ImportError:
        raise RuntimeError(
            "stable-audio-3 not installed.\n"
            "1. git clone https://github.com/Stability-AI/stable-audio-3.git\n"
            "2. cd stable-audio-3 && uv sync --extra ui   # or your preferred\n"
            "3. cd ../forage-dj && uv pip install -e ../stable-audio-3\n"
            "Or see scripts/setup.sh --help for the automated helper."
        ) from None

    # TODO (swarm agent): 
    # model = StableAudioModel.from_pretrained(f"stabilityai/stable-audio-3-{model}")
    # audio = model.generate(prompt=..., duration=duration, seed=seed, ...)
    # out = Path.home() / ".foragedj" / "generated" / f"{seed}_{prompt[:30]}.wav"
    # torchaudio.save(...) + embed metadata with prompt + SAFETY_NOTE + timestamp
    # return out

    raise NotImplementedError("Phase 1 swarm task: replace this stub with real Stable Audio 3 call + seed + cache + metadata.")
```

This skeleton is copy-paste ready for the first subagent. Embed SAFETY_NOTE on every generated file (WAV metadata or sidecar JSON).

---

## Appendix C: Post-Approval First 10 Todo Items (for todo_write)

1. Fix pyproject.toml + add .python-version
2. Create scripts/setup.sh + make executable
3. Create LICENSE + update .gitignore
4. Scaffold all 10+ new src/ modules with correct contracts
5. Rewrite cli.py with subcommands + doctor
6. Update README + 4 agent/docs files (Phase 0 complete)
7. Run full validation sequence (install uv, sync, doctor, imports, pytest skeleton)
8. Generate + commit uv.lock + first hygiene commit
9. Spawn 4+ parallel swarm subagents for Phase 1 issues (with full context)
10. MCP GitHub sync: comment progress on issues #1-4 + create SWARM_STATUS.md

Mark complete immediately after each. Use merge=true for incremental updates.

---

## Appendix D: MCP GitHub Usage Reminder (for swarm coordination)

Before any `use_tool` call:
1. `search_tool(query="github create issue OR comment")` → inspect schemas
2. Use exact param names from the returned schema (never guess)
3. Prefer `add_issue_comment` / `create_pull_request` for swarm visibility

Example flow after subagent delivers a module:
- Push branch (via terminal or future MCP)
- Open PR
- `use_tool( tool_name=..., tool_input={...} )` to post "Swarm agent completed audio_gen.py — ready for review. Links to acceptance in plan.md"

This keeps the public GitHub swarm alive exactly as README advertises.

