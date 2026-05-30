# Enhancement, Voice & Audio Tools — Sonic Forage 2025 Stack

This extends the core generative DJ system with **production-grade audio restoration, cleaning, and vocal synthesis** tools.

Everything lives under `checkpoints/enhancers/` and `checkpoints/voice/` on your Z: drive.

## Quick Start

```bash
# 1. Download the new tools (most are small/open)
uv run python scripts/download_checkpoints.py --group enhancers
uv run python scripts/download_checkpoints.py --group voice

# 2. (Optional but recommended) Install runtime extras
uv sync --extra audio-tools --extra stems

# 3. Use them
foragedj enhance my_lowres_track.wav --model flashsr-tiny
foragedj clean-voice noisy_vocal.wav
foragedj speak "drop the bassline dominion" --voice af_heart
foragedj split-stems full_mix.wav
```

## The Models

### Super-Resolution / Enhancement

| Model | Size / Speed | Best For | Notes |
|-------|--------------|----------|-------|
| **YatharthS/FlashSR** (tiny) | 2 MB / 500 KB, **200-400× realtime** | Live enhancement, batch upscaling of generations | The speed king. 16 kHz → 48 kHz. ONNX or small torch path. |
| **laion/FlashSR One-step** (2025 distilled) | ~3 GB total, very fast single pass | High quality post-processing of generated libraries | Excellent quality/speed tradeoff vs original AudioSR. Standalone enhance.py available. |
| **drbaph/AudioSR** (basic + speech) | ~6 GB each, 50-100 diffusion steps (~0.6× RT) | Maximum perceptual fidelity on important masters | Latent diffusion. Use ComfyUI-AudioSR node or the original haoheliu repo for best results. Two variants (general vs speech/vocals). |

**Recommendation**: Default to `flashsr-tiny` for daily work. Use the laion one-step or AudioSR when you want to "print" a final polished version of a set.

### Voice Quality Enhancement — LocalVQE (LocalAI-io)

- **Not TTS** (common mix-up). This is a tiny causal streaming model for:
  - Acoustic Echo Cancellation (AEC)
  - Noise Suppression
  - Dereverberation
- Two sizes: 1.3 M params (~5 MB) or 4.8 M (~19 MB) GGUF.
- Runs 5–10× realtime on CPU with ~16 ms latency.
- Perfect for cleaning vocal samples, live mic input into the DJ station, or processing AI-generated voice elements.
- Best runtime: compile the C++/GGML engine from https://github.com/localai-org/LocalVQE (nix flake or cmake). GGUF files are in `checkpoints/voice/localvqe/`.

### TTS / Vocal Elements — Kokoro-82M (hexgrad)

- 82 M parameters, Apache 2.0.
- Surprisingly high quality for its size. Streaming capable, <250 ms latency possible.
- 50+ voices across languages (see VOICES.md on the HF repo).
- Excellent for:
  - Spoken intros / announcements
  - Robotic / processed vocal chops
  - Text-to-layer material you then enhance + mix
- Install: `uv pip install kokoro soundfile` + `espeak-ng` (system).
- Command: `foragedj speak "text here" --voice af_heart`

## Stem Separation (Demucs + RoFormers)

Already wired via the `stems` extra (`demucs` package).

```bash
uv sync --extra stems
foragedj split-stems my_track.wav
```

Outputs 4-stem (or 6-stem) folders. Isolate vocals for RVC conversion, drums for breaks, etc.

Community SOTA vocal models (Mel-Band RoFormer / BS-RoFormer from pcunwa, ZFTurbo etc.) can be added later via the `audio-separator` library or UVR-style ONNX packs.

## Integration Points in the OS

- `foragedj os` → chunky buttons: **Enhancer** and **Voice Lab**
- All tools output into `test_outputs/enhanced/`, `cleaned/`, `tts/`, `stems/`
- Enhanced / cleaned / generated voice files drop straight into `libraries/` for `play-library` or `live` mode.
- Future: wire enhancers as post-processing step inside `generate-setlist` and `live` lookahead.

## Hardware Notes

- FlashSR tiny + LocalVQE + Kokoro all run great on potato CPUs/GPUs.
- AudioSR and the larger FlashSR one-step prefer 6–12 GB+ VRAM for comfortable use.
- Everything respects the Z: drive `.grok/hf-cache.env` pinning.

## Next-Level Ideas (Agentic / DAW)

- Auto-enhance every track at the end of `generate-setlist`
- Real-time enhancer insert on the live mixer decks
- Voice Lab → generate call-and-response vocals that the agent then mixes intelligently
- Stem-split → RVC conversion pipeline for instant singer swaps on library tracks

See also:
- `docs/MODEL_ACCESS.md` (license steps)
- `src/foragedj/enhance.py` (the actual wrappers)
- The individual HF model cards for the latest inference notebooks / ComfyUI nodes.

Happy enhancing. Your generations just got a mastering suite. 🎛️🔊
