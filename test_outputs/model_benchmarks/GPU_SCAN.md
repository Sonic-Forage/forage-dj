# GPU & Environment Scan — ForageDJ Music Generation

**Date**: 2026-05-30
**Purpose**: Determine realistic performance expectations for local Stable Audio 3 generation.

## Detected Hardware

From nvidia-smi (run at scan time):
- GPU 0: NVIDIA GeForce RTX 4070
- VRAM: 12 GB (12282 MiB)
- Driver: 596.36
- CUDA: 13.2
- Current usage (idle): ~1.4 GB (mostly desktop / Xwayland)

## PyTorch / Inference Stack Status

**Current state in this venv**:
- torch is **NOT INSTALLED**
- stable-audio-3 is **NOT INSTALLED**

This is expected during active development (the project keeps the heavy inference stack optional so `uv sync` stays fast).

## Model Inventory (all present on Z: drive)

Core Stable Audio 3 models:
- stable-audio-3-small-music (2.2 GB) — Excellent quality, very fast
- stable-audio-3-small-sfx (2.2 GB) — Great for risers, impacts, textures
- stable-audio-3-medium (8.6 GB) — Highest quality, more VRAM hungry

Autoencoders (SAME):
- SAME-S
- SAME-L

LoRAs downloaded (5+):
- Several SA3-specific LoRAs (loopwyrm, ltx23-sfx-drops, etc.)
- Some ComfyUI-style ones

Enhancers / Voice tools: partially downloaded (work in progress)

## Realistic Expectations on RTX 4070 12GB

Once torch + stable-audio-3 are installed:

**Small models (small-music, small-sfx)**:
- 15-30s generation: typically 4–12 seconds wall time on this GPU
- Very low VRAM usage (~2-4 GB)
- Excellent for real-time / live performance workflows

**Medium model**:
- 15-30s generation: ~15–40 seconds depending on settings
- VRAM: 6–9+ GB
- Highest fidelity — worth it for final tracks

**With your current hardware you can comfortably**:
- Run full ForageDJ workstation (mixer + GUI + visualizer + generation)
- Generate while mixing
- Use medium model without swapping
- Run multiple small generations in parallel if desired

**Potato / CPU fallback**:
- Small models still work acceptably on CPU (slower, ~30-90s for 30s audio)
- Medium will be painful on CPU

## Recommended Next Steps

1. Install the inference stack (one-time, ~10-20 min):
   ```bash
   git clone https://github.com/Stability-AI/stable-audio-3.git /mnt/z/IMF2045/stable-audio-3
   cd /mnt/z/IMF2045/stable-audio-3
   uv sync --extra ui
   cd /mnt/z/IMF2045/forage-dj
   uv pip install -e /mnt/z/IMF2045/stable-audio-3
   ```

2. Run the benchmark:
   ```bash
   uv run python test_outputs/model_benchmarks/run_model_speed_test.py
   ```

3. During generation, keep `nvidia-smi -l 1` open in another terminal to watch VRAM.

## Current Workarounds (while torch is missing)

You can still do full dry-run testing and manifest validation:
```bash
uv run foragedj generate "test prompt" --model small-music --dry
uv run foragedj generate-setlist --manifest setlists/bassline_dominion_seed424242.yaml --dry
```

All metadata, session, and distribution tooling works today.
