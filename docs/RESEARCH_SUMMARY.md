# Research Summary — forage-dj

All research conducted May 30, 2026 for the Sonic Forage DJ project. Sources verified via web search and direct repo inspection.

## 1. Stable Audio 3 (Stability AI, May 2026 Release)

**Key Models**:
- `stabilityai/stable-audio-3-small-music` (0.6B) — CPU-friendly, ≤120s, music-focused. Ideal for potato machines.
- `stabilityai/stable-audio-3-small-sfx` (0.6B) — Same, optimized for sound effects / pads / samples.
- `stabilityai/stable-audio-3-medium` (2B) — GPU recommended, up to ~380s, higher quality.

**Inference**:
- Official repo: https://github.com/Stability-AI/stable-audio-3
- Python lib: `from stable_audio_3 import StableAudioModel`
- CLI: `stable-audio --model small-music -p "..." --duration 60 -o track.wav`
- Gradio UI included.
- Supports text-to-audio, audio-to-audio editing, inpainting/continuation, LoRA fine-tuning at runtime.
- Hardware: Small models run on Mac CPU in ~6s for 120s audio. Medium needs ~5-6GB VRAM.
- Prefix prompts with "TrackType: Music, ..." or "TrackType: SFX" for best results.

**Why Perfect**: Fast enough for live-ish generation, open weights, variable length, editing modes = perfect for DJ workflow (generate intro, then continue with variation).

## 2. Open-Source DJ Software Reference

**Mixxx** (https://mixxx.org/)
- Best free/open-source DJ app (Windows/Mac/Linux).
- 4 decks, sync, waveforms, beatgrid, hotcues, loops, 3-band EQ + filter, effects, AutoDJ.
- Excellent MIDI/HID controller support with programmable mappings (JS scripting).
- Community NS7II mapping exists (see Mixxx discourse).
- Great UI/UX reference for deck layout, visual feedback, library.

**Serato DJ / VirtualDJ** (commercial reference)
- 4-deck layouts, stem separation (paid), extensive effects, key matching (Camelot), video support.
- NS7II native (Serato).
- Our goal: replicate core feel + add AI generation layer.

**Other Inspirations**:
- DawDreamer (Python DAW with JUCE)
- Web Audio API + Tone.js projects for browser DAW ideas
- Existing AI DJ experiments (ElMoorish/AI-DJ-Software etc.)

## 3. Hardware: Numark NS7II

- 4-deck turntable platter controller with high-res MIDI.
- Designed for Serato (full integration + visual feedback).
- Fully MIDI mappable for other software.
- Existing Mixxx mapping: https://mixxx.discourse.group/t/numark-ns7-ii-mapping-numark-ns7-2/24674 (XML + Excel).
- Key controls: Platters (jog/scratch), faders (volume/EQ), buttons (cue/play/hotcue/effects), touch FX.
- Plan: Map core functions + add MIDI Learn for user customization.

## 4. Audio Tools

**AudioSR** (https://huggingface.co/spaces/haoheliu/audiosr_versatile_audio_super_resolution)
- Latent diffusion upscaler: low-res → 48kHz high-fidelity.
- Perfect post-process for generated tracks or imported low-quality stems.
- HF model available; easy pipeline integration.

**Demucs / Audio Separator**
- State-of-the-art stem separation (drums, bass, vocals, other).
- Python package: `demucs` or `audio-separator`.
- Use case: Generate track → split stems → load individual stems to sampler pads for live remixing.

## 5. Sonic Forage Ecosystem (Your Existing Work)

**Org**: https://github.com/Sonic-Forage

**Key Repos**:
- `sonic-forage-autonomous-dj-os`: "World's first autonomous DJ operating system" — Ralph loop, payloads, voice/ComfyUI contracts, closed gates, safety framework. **Primary integration target**.
- `sonicforge-starter-kit`: Launch cockpits for AI DJ agents.
- `sonic-forage-master-prompt-arcade`: Prompt library, tag taxonomy, Unicode UI kit.
- `rave-harm-reduction-community-kit`: Public-safe educational content.
- `sonic-forage-asset-vault`, `sonic-forage-autonomous-booking-kit`, etc.

**Integration Plan**: Import or submodule the autonomous-dj-os logic for the agent layer. Use its safety gates for any autonomous actions. Reuse prompt styles and persona system.

## 6. Additional Tech Research

- **MIDI in Python**: `mido` (high-level) + `python-rtmidi` (low-level, cross-platform).
- **Real-time Audio**: `sounddevice` (PortAudio wrapper), `python-rtmixer` (low-latency mixer), `pedalboard` (Spotify's effects/EQ).
- **GUI Options**: Dear PyGui (immediate mode, fast for audio apps), PyQt6, Tauri (Rust + web frontend for lighter install).
- **Voice**: `faster-whisper` (tiny model ~39MB, fast STT), Ollama for local LLM intent parsing.
- **Analysis**: `librosa` (BPM, key, onset, chroma — industry standard).

## 7. Gaps & Future Research Needed
- Real-time stem separation latency (current Demucs is offline; look for streaming alternatives later).
- Beat-perfect sync across generated tracks (librosa + phase vocoder or rubberband).
- LoRA training UX for user style personalization.
- Multi-user / collab mode (future).

**All links and models verified live on 2026-05-30.**

*Research compiled by Grok + team for Sonic Forage. Ready to build.*
