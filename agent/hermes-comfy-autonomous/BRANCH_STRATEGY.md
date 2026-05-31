# Branch Strategy

We are using a deliberate three-branch model to keep development clean while preserving history.

## 1. `main` (Primary Development Line)

**Purpose**: The current recommended version of ForageDJ.

**Focus**:
- ComfyUI as the primary (and eventually only) high-quality music generation engine.
- ACE-Step 1.5 XL Turbo and other strong ComfyUI audio workflows.
- Excellent support for both local (Tailscale) and remote (RunPod, Vast, etc.) ComfyUI servers.
- Autonomous / background generation features.
- The terminal radio and player experiences as first-class consumers of generated music.

**Rules**:
- Only high-quality ComfyUI-driven work goes here.
- The old Python Stable Audio backend is **not** developed here.

## 2. `legacy/stable-audio`

**Purpose**: Complete preservation of all previous Stable Audio Python backend work.

**Contents** (snapshot as of the pivot):
- All Python code related to stable-audio-3 (small-music, small-sfx, medium, open, etc.).
- Related experiments, training code, LoRAs, and the old `generate_track` Python implementation.
- Old documentation and setup instructions for the Python path.

**Why it exists**:
- Some people may still want or prefer the old Python backend.
- Historical record of what was tried.
- Prevents the main codebase from being polluted with code we're no longer investing in.

**Rules**:
- This branch is mostly frozen.
- Only critical fixes or documentation improvements. No new features.
- Do not merge code from this branch into `main` or `beta` unless explicitly approved.

## 3. `beta`

**Purpose**: Experimental sandbox.

**What belongs here**:
- Wild ideas
- Early prototypes
- Risky architectural experiments
- New model integrations that aren't proven yet
- Experimental radio interfaces or autonomous behaviors

**Rules**:
- Can be unstable.
- Should generally be branched from `main`.
- When something proves itself, it can be merged into `main` after review.

## How to Choose Where to Work

- Normal development → `main`
- Anything related to the old Python Stable Audio models → `legacy/stable-audio`
- Crazy / early / high-risk stuff → `beta`

When creating autonomous sessions or tasks, always tag them with the target branch.

## Communication Rule

Any agent or human working across branches must clearly state which branch they are modifying in every commit message and status update.
