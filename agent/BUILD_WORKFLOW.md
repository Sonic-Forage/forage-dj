# 🔧 BUILD_WORKFLOW.md - Autonomous Step-by-Step Build Plan

**Follow this workflow exactly. Do not skip steps.**

## Phase 0: Setup & Verification (Do this first)

1. Clone the repo (if not already local)
2. Run `uv sync --extra cpu`
3. Verify all dependencies install cleanly
4. Create `src/foragedj/__init__.py` and `src/foragedj/cli.py` if missing
5. Test that `uv run foragedj --help` works (even if it just prints version)

**Acceptance**: Clean install + basic CLI entry point exists

## Phase 1: Audio Generation Core (Stable Audio 3 + Seed)

**Goal**: User types prompt + seed → generates 30-60s audio file

### Steps:
1. Install `stabilityai/stable-audio-3` (already in pyproject.toml)
2. Create `src/foragedj/generation.py`
   - Function: `generate_track(prompt: str, seed: int, duration: float = 45.0)`
   - Use small-music model for CPU
   - Save to `outputs/tracks/`
3. Add seed control and prompt embedding
4. Test generation on CPU (should take <2min for 45s track)

**Acceptance**: Can generate a track from prompt + seed and save as .wav

## Phase 2: 2-Deck Mixer

**Goal**: Load two tracks and mix them live

### Steps:
1. Create `src/foragedj/mixer.py`
   - Use `sounddevice` + `pedalboard` for real-time playback
   - Volume, 3-band EQ, low-pass filter, crossfader
2. Basic two-deck class with play/pause, load, crossfade
3. Test with two generated tracks

**Acceptance**: Two tracks play simultaneously with working crossfader

## Phase 3: Simple GUI (Prototype)

**Goal**: User-friendly interface to test everything

### Options (choose one):
- Dear PyGui (fast, native) — recommended for potato machines
- Gradio (quick web prototype)

Create `src/foragedj/gui.py` with:
- Prompt input + Seed slider
- "Generate Track" button
- Deck A / Deck B with load + play controls
- Mixer sliders (volume, EQ, filter, crossfader)

**Acceptance**: GUI launches and all controls work

## Phase 4: Setlist Runner (Core Innovation)

**Goal**: User gives list of prompts → full set generated with shared seed

Create `src/foragedj/setlist.py`
- Parse list of prompts
- Generate each with incremental seeds or shared seed
- Auto crossfades between tracks

**Acceptance**: 3-prompt setlist generates a coherent mini-mix

## Phase 5: Testing & Polish

1. Run full test suite on CPU-only machine
2. Add basic error handling and safety notes
3. Update README with working demo instructions
4. Create first release tag (v0.1-mvp)

---

**Current Status**: Phase 0 ready to start.

**Next action for you**: Begin Phase 0 now.

When each phase is complete, update this file with [x] and commit.

**You have full autonomy. Build.**