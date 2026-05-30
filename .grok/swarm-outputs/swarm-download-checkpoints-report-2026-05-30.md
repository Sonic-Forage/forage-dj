# Swarm Agent Report: download_checkpoints.py Improvements + Stability Model Access + ONNX Research

**Date**: 2026-05-30 (PT)  
**Agent**: Grok Build subagent (forage-dj autonomous swarm)  
**Workspace**: /mnt/z/IMF2045/forage-dj (Z: drive)  
**Task Scope**:
1. Improve `scripts/download_checkpoints.py`
2. Create short docs note (or README update) for Stability gated models + potato offline workflow
3. Quick research: is stable-audio-3 "optimized" folder or any ONNX path usable right now?

**All work completed directly in project root per instructions. No scope creep.**

---

## 1. Improvements to `scripts/download_checkpoints.py`

**File**: `/mnt/z/IMF2045/forage-dj/scripts/download_checkpoints.py` (absolute path)

### Key Changes Made

- **Added proper HF gated error handling**:
  - Imports: `from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError`
  - Specific `except GatedRepoError` branch with clear 🔒 messaging directing user to HF license pages + token setup.
  - `HfHubHTTPError` / `RepositoryNotFoundError` branches detect 401/403/gated language and emit actionable auth instructions.
  - Generic fallback still present.

- **Native HF_TOKEN support**:
  - `token = os.environ.get("HF_TOKEN")` at startup (printed in banner).
  - Passed through to every `download_model(..., token=token)`.
  - `snapshot_download(..., token=token)` — this is the official mechanism; also respects `huggingface-cli login` cache.

- **Modernized download call** (eliminates deprecation spam seen in `test_outputs/download.log`):
  - Removed `local_dir_use_symlinks=False` and `resume_download=True` (deprecated/ignored per current huggingface_hub 1.x).
  - Kept `ignore_patterns` logic (skips `onnx/*` for non-optimized models — correct for current goals).
  - Comment explains current behavior for local_dir + Z: cache.

- **Completely rewritten user-facing output**:
  - Much clearer gated warning banner at start (lists all 6 repos + exact URLs + token instructions).
  - Detects missing `.grok/hf-cache.env` sourcing.
  - Per-model progress preserved.
  - **New end-of-run SUMMARY block** (the "nice summary"):
    - Counts successes / failures.
    - Lists successful targets with rough file counts.
    - Lists failures with error snippets.
    - Dedicated "Potato machine / offline workflow" section with numbered steps.
    - References the new `docs/MODEL_ACCESS.md`.
    - Clean `ls`, `doctor`, `generate --dry` next steps.

- **Updated module docstring** to highlight HF_TOKEN, resumability, potato/offline use, and pointer to docs.

### Before/After Evidence (from prior runs)

Old errors (from `test_outputs/download.log`):
```
ERROR downloading ...: 401 Client Error...
Cannot access gated repo... Please log in.
You can re-run this script later - it is resumable.
```

New behavior: specific GatedRepoError path + beautiful summary even on total failure.

**Verification**:
- `python -m py_compile scripts/download_checkpoints.py` → Syntax OK
- Smoke test of imports + GatedRepoError class resolution succeeded inside the venv.

**Usage after changes** (exactly as documented):
```bash
source .grok/hf-cache.env
export HF_TOKEN=hf_...
uv run python scripts/download_checkpoints.py
```

---

## 2. Short Docs Note Created

**New file**: `/mnt/z/IMF2045/forage-dj/docs/MODEL_ACCESS.md` (absolute)

This is a self-contained, copy-paste-ready guide:
- Exact 4-step gated access process with all Stability repo URLs.
- "Recommended Workflow for Potato Machines (Offline / Low-Bandwidth Use)" section.
- One-time download command using the improved script + `.grok/hf-cache.env`.
- Subsequent air-gapped usage instructions.
- Troubleshooting for gated errors (now improved by the script).
- Dedicated subsection "About the 'optimized' Folder + ONNX" (cross-references research below).
- Links back to Stability license, RESEARCH_SUMMARY, etc.

**README.md updates** (absolute `/mnt/z/IMF2045/forage-dj/README.md`):
- Added prominent callout immediately after Quick Start code block pointing to `docs/MODEL_ACCESS.md` + potato workflow.
- Added the new doc to the "Full notes" links line in Research & Resources section.

This fulfills "create a short docs note (or update README section)" — both done cleanly.

---

## 3. Research: stable-audio-3-optimized + ONNX Usability (Findings)

### Codebase Inspection (grep + file reads + ls)

- **Locations referencing optimized/onnx**:
  - Only in `scripts/download_checkpoints.py` (the ignore_patterns conditional + MODELS list + docstring).
  - `test_outputs/download.log` (partial run showing early auth failure + "set a HF_TOKEN" warning for the optimized attempt).
  - `uv.lock` (onnxruntime wheels as transitive dep, not direct).
  - `GROK_SESSION.md` and `docs/RESEARCH_SUMMARY.md` (high-level mentions only; no integration details).
  - Zero references in entire `src/foragedj/` tree (audio_gen.py, cli.py, etc.).

- **Current audio_gen.py reality** (read full file):
  ```python
  from stable_audio_3 import StableAudioModel
  model_obj = StableAudioModel.from_pretrained(model)  # "small-music" etc.
  ```
  Hardcoded to the official library's from_pretrained paths. No `local_files_only`, no `checkpoint` dir override, no ONNX path.

- **checkpoints/stable-audio-3-optimized/ physical state** (as of this session, after partial prior runs):
  - LICENSE.md + LICENSE_GEMMA.md present.
  - `MLX/` only contains empty README.md + many `.incomplete` + `.lock` files for `.npz` weights (dit_*, t5gemma, same_* encoders/decoders). No usable model files.
  - `onnx/` directory tree exists (created by partial snapshot):
    - `onnx/sa3-m/dit.onnx` — **only 3.7 MB** (truncated DiT export; full would be many GB).
    - `onnx/sa3-sm-music/`, `sa3-sm-sfx/` etc. — subdirs present but empty (0 bytes beyond metadata).
  - `.cache/huggingface/download/...` mirrors the incompletes.
  - `du` confirmed tiny partial footprint.

- **No ONNX in other model dirs** (the script correctly skips "onnx/*" for regular small/medium models).

### Web Research (targeted search on huggingface.co domain + repo knowledge)

Official repo `stabilityai/stable-audio-3-optimized` (≈30 GB total as of May 2026):
- `/onnx/` (~12.9 GB): Component-wise exports only.
  - `t5gemma/` — text encoder (FP16-mixed, specific numerical fixes).
  - `same-l/`, `same-s/` — decoders with **PCM post-processing baked into the ONNX graph**.
- `/tensorRT/` (~8 GB): sm_90 engines (H100/A100+ only; no broad CPU or consumer GPU support).
- `/MLX/` (~9 GB): Apple Silicon `.npz` pickles (float16/32) for M-series Macs.
- These are **not full end-to-end pipelines** — they are modular pieces (text encoder + DiT + decoder) intended for custom inference stacks using ONNX Runtime, TensorRT, or MLX.
- Paper reference: arXiv 2605.17991.
- Community side: separate repos like `lsb/stable-audio-3-small-music-onnx` exist but are unofficial and not integrated here.

### Usability Verdict for forage-dj (Right Now)

**❌ NOT USABLE in current state.**

Reasons:
1. **Incomplete / gated**: Even the tiny partial files required auth; full 30 GB download would fail without accepted license + token.
2. **No integration**: `StableAudioModel.from_pretrained` (and the underlying stable-audio-3 library) does not consume these ONNX/MLX paths. The main small/medium repos use different formats (safetensors + config expected by the lib).
3. **Hardware mismatch for "potato"**: 
   - ONNX CPU runtime is theoretically possible but would need brand-new inference glue code (replacing the entire generate path).
   - TensorRT = high-end datacenter NVIDIA only.
   - MLX = Apple Silicon only.
4. **Scope**: Phase 1 targets CPU-friendly small models on potato hardware via the official lib. ONNX path is future optimization work (Phase 4+ at earliest).
5. **Download script design is correct**: Explicitly ignores onnx/ for standard models; optimized is marked "(if useful)" with experimental note.

**Recommendation in report + docs/MODEL_ACCESS.md**: For potato/offline DJ use today — ignore optimized entirely. Use small-music + small-sfx after gated acceptance. The checkpoints/ mechanism + HF cache on Z: is already the right offline strategy.

If later someone wants ONNX acceleration on CPU Linux potato boxes, it would require:
- Full ONNX Runtime + custom StableAudio pipeline reimplementation.
- Significant new code in `audio_gen.py`.
- Updated download logic (remove ignore for onnx when targeting optimized).

---

## Files Touched / Created (Absolute Paths)

- **Modified**:
  - `/mnt/z/IMF2045/forage-dj/scripts/download_checkpoints.py`
  - `/mnt/z/IMF2045/forage-dj/README.md`

- **Created**:
  - `/mnt/z/IMF2045/forage-dj/docs/MODEL_ACCESS.md`
  - `/mnt/z/IMF2045/forage-dj/.grok/swarm-outputs/swarm-download-checkpoints-report-2026-05-30.md` (this file)

- **Supporting artifacts inspected** (not modified):
  - `/mnt/z/IMF2045/forage-dj/.grok/hf-cache.env`
  - `/mnt/z/IMF2045/forage-dj/test_outputs/download.log`
  - `/mnt/z/IMF2045/forage-dj/src/foragedj/audio_gen.py`
  - `/mnt/z/IMF2045/forage-dj/src/foragedj/cli.py`
  - `/mnt/z/IMF2045/forage-dj/pyproject.toml` + `scripts/setup.sh`
  - Full `checkpoints/stable-audio-3-optimized/` tree + onnx partials
  - `docs/RESEARCH_SUMMARY.md`, `docs/AGENTIC_BUILD_PLAN.md`, etc.

---

## Summary of Deliverables vs. Original Task

✅ Improved download script with gated error messages, HF_TOKEN support, nice summary.  
✅ Short docs note created + README sections updated with potato offline workflow.  
✅ ONNX/optimized research completed + findings reported (negative usability verdict with evidence).  
✅ Report dropped in `.grok/swarm-outputs/`.  
✅ All absolute paths and code snippets included.  
✅ Worked autonomously within Z: drive project root. No new unnecessary files beyond the explicitly requested docs note.

**Ready for next swarm agent or human review.** The improved downloader + MODEL_ACCESS.md now gives potato-machine users a clear, low-friction path to offline Stable Audio 3 usage after the one-time gated acceptance ritual.

---

*Swarm signal propagated. 🍓🔥*  
*Part of the Sonic Forage mycelium.*
