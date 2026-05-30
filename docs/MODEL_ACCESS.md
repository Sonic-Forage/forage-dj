# Model Access & Offline Workflow — forage-dj

**Stability AI models (Stable Audio 3 family) are gated on Hugging Face.**  
You must explicitly accept the license for each repo before downloads or inference will succeed.

## Required One-Time Steps (Gated Access)

1. **HF Account**  
   Free signup: https://huggingface.co/join

2. **Accept Licenses** (do this for every model you plan to use)  
   Visit and click **"Agree and access repository"** on each:
   - https://huggingface.co/stabilityai/stable-audio-3-small-music
   - https://huggingface.co/stabilityai/stable-audio-3-small-sfx
   - https://huggingface.co/stabilityai/stable-audio-3-medium
   - https://huggingface.co/stabilityai/stable-audio-3-optimized (experimental variants)
   - https://huggingface.co/stabilityai/SAME-S
   - https://huggingface.co/stabilityai/SAME-L

   These are the **SAME autoencoders** + main diffusion models used by the `stable-audio-3` library.

3. **Get a Token**  
   Go to https://huggingface.co/settings/tokens  
   Create a new token (fine-grained "Read" access to the Stability repos is sufficient).  
   Copy the `hf_...` string.

4. **Authenticate in Your Environment**
   ```bash
   # Option A (recommended for sessions)
   export HF_TOKEN=hf_your_token_here

   # Option B (persists across terminals)
   huggingface-cli login
   ```

## Recommended Workflow for Potato Machines (Offline / Low-Bandwidth Use)

Potato machines (8-16 GB RAM, integrated graphics or weak CPU) should use the **small** models. The download script + Z: drive cache makes everything offline-friendly after one good connection.

### One-Time Setup (on a machine with decent internet)

```bash
cd forage-dj

# 1. Pin large files to the Z: drive (or your big disk)
source .grok/hf-cache.env

# 2. Provide token for gated models
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx

# 3. Run the downloader (resumable, shows nice gated error messages + final summary)
uv run python scripts/download_checkpoints.py
```

This creates:
- `checkpoints/stable-audio-3-small-music/` etc. (direct copies)
- Full HF cache under `.cache/huggingface/` on the same drive

**Total size**: ~ few GB for the small models + autoencoders. Optimized repo is much larger (30+ GB) and mostly for accelerators.

---

## New 2025 Enhancement & Voice Stack (AudioSR, FlashSR, LocalVQE, Kokoro)

These are mostly **open weights** (Apache 2.0 or MIT). No license clicking required for most, but always check the individual model card.

### Audio Super-Resolution / Enhancement

**FlashSR family (strongly recommended)**

- **YatharthS/FlashSR** (the tiny one)
  - https://huggingface.co/YatharthS/FlashSR
  - 2 MB PyTorch / 500 KB ONNX. 200-400× realtime 16 kHz → 48 kHz.
  - Best daily driver for the OS.

- **laion/FlashSR_One-step_Versatile_Audio_Super-resolution** (2025 distilled paper model)
  - https://huggingface.co/laion/FlashSR_One-step_Versatile_Audio_Super-resolution
  - ~3 GB total (student LDM + vocoder + VAE). Excellent quality in a single fast pass.
  - Has a ready-to-run `enhance.py`.

- **drbaph/AudioSR** (and original haoheliu)
  - https://huggingface.co/drbaph/AudioSR
  - ~5.9 GB per variant (`audiosr_basic_fp32.safetensors` for music/general, `_speech_` for vocals).
  - Highest quality but slow diffusion (use ComfyUI-AudioSR node or https://github.com/haoheliu/versatile_audio_super_resolution).

### Voice Quality Enhancement (LocalVQE)

- **LocalAI-io/LocalVQE** — https://huggingface.co/LocalAI-io/LocalVQE
  - **Not TTS**. Real-time causal model for joint Acoustic Echo Cancellation + Noise Suppression + Dereverberation.
  - GGUF files only 5–19 MB. 5–10× realtime on CPU.
  - Download the GGUF via the downloader or directly. Best speed = build their tiny C++ GGML engine (nix flake provided).
  - Perfect for cleaning samples and live mic input inside the DJ workstation.

### Lightweight High-Quality TTS (Kokoro)

- **hexgrad/Kokoro-82M** — https://huggingface.co/hexgrad/Kokoro-82M
  - 82 M params, Apache 2.0, streaming, many voices.
  - `pip install kokoro soundfile` + system `espeak-ng`.
  - Auto-downloads into your pinned HF cache on first use.
  - Command: `foragedj speak "text" --voice af_heart`
  - Outstanding for voiceovers, drops, and generative vocal material.

Run the downloader with `--group enhancers` or `--group voice` (or just `--group all`) to populate `checkpoints/enhancers/` and `checkpoints/voice/`.

Full usage + integration guide: **docs/ENHANCEMENT_TOOLS.md**

These tools make the "Music Diffusion OS" a complete production workstation, not just a generator.

### Subsequent Use (Air-Gapped, Offline, or Reboots)

- The same `source .grok/hf-cache.env` ensures all future HF operations (including inside `stable-audio-3` lib) hit your local Z: cache.
- No re-downloading of multi-GB files.
- Small models run acceptably on CPU for generation (target <30s wall time for 60s audio per Phase 1 goals).

```bash
source .grok/hf-cache.env
uv run foragedj doctor
uv run foragedj generate "uplifting house 128bpm intro" --seed 424242
```

## About the "optimized" Folder + ONNX

See research notes in the swarm report. In short:
- Contains experimental MLX (Apple), TensorRT (high-end NVIDIA), and ONNX component exports.
- ONNX files (~13 GB) are split (text encoder + decoders) with baked post-processing.
- **Not currently usable** as a drop-in replacement in forage-dj or the standard `stable-audio-3` Python library.
- The download script skips `onnx/*` for the regular models by design.
- Useful only if you are doing custom acceleration work later (Phase 4+).

For normal potato-machine DJ use: **stick to small-music + small-sfx** after accepting their gates.

## Troubleshooting Gated Errors

The improved `scripts/download_checkpoints.py` now detects `GatedRepoError`, 401/403, etc. and prints exact next steps.

Common fixes:
- Double-check you clicked "Agree" while **logged in** on the exact model page.
- Token must come from the same account that accepted.
- Re-export `HF_TOKEN` after `huggingface-cli login` in new shells.
- Re-run the downloader — it is fully resumable.

## References
- Stability AI Community License: https://stability.ai/license
- Official stable-audio-3 repo: https://github.com/Stability-AI/stable-audio-3
- Main project README + docs/RESEARCH_SUMMARY.md

*Part of the Sonic Forage mycelium — keep it public-safe.*
