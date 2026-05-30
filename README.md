# forage-dj

**Sonic Forage DJ** — Open-source AI-powered autonomous DJ interface & DAW

Prompt-to-track generation • Stable Audio 3 integration • Numark NS7II / MIDI controller support • Real-time mixing • Auto-mix agent • Voice commands • Built on the Sonic Forage mycelium for rave culture, safety gates & creative AI agents.

[![License: Community](https://img.shields.io/badge/License-Stability%20AI%20Community-blue)](https://stability.ai/license)

## Vision

ForageDJ turns your computer (even potato machines) into a full autonomous DJ rig. Generate tracks on-the-fly with Stable Audio 3 small models, mix them live with hardware controllers, let AI handle transitions, drop SFX pads, and keep the rave safe & fun with built-in harm-reduction prompts and gates from the Sonic Forage ecosystem.

Fork it. Remix it. Play it. Grow the scene.

## Quick Start (MVP)

```bash
# Clone
 git clone https://github.com/Sonic-Forage/forage-dj.git
 cd forage-dj

# Setup (uv recommended - fast, like your other Sonic-Forage repos)
 uv sync --extra cpu   # or --extra cuda for GPU

# Run the app (placeholder until full MVP)
 uv run foragedj
```

**Current Status**: Foundational repo with full research, architecture, agentic build plan, and specs. MVP in active development (see AGENTIC_BUILD_PLAN.md).

## Key Features (Roadmap)

### MVP (v0.1 - 2 weeks)
- 2 virtual decks with prompt-to-WAV generation (Stable Audio 3 small-music / small-sfx)
- Real-time mixer: volume, 3-band EQ, filter, crossfader (sounddevice + pedalboard)
- Numark NS7II MIDI mapping + MIDI Learn
- Basic waveform + BPM/key detection (librosa)
- Auto-mix mode (simple beat-matched transitions)
- Voice commands (tiny Whisper + local LLM)
- Post-process: AudioSR upscale + Demucs stems

### v0.5
- 4 decks + sampler pads
- Hotcues, loops, effects chain
- Full integration with sonic-forage-autonomous-dj-os (Ralph loop, payloads, safety gates)
- Touch OSC support
- Library browser with generated tracks

### v1.0+
- LoRA fine-tuning UI
- Community vault sync
- Freemium cloud tier (faster models, extra LoRAs)
- Web version / Tauri desktop

## Tech Stack

- **Python 3.12** (uv + pyproject.toml)
- **Audio Gen**: stabilityai/stable-audio-3 (small-music, small-sfx, medium) + official inference lib
- **Mixing Engine**: sounddevice + python-rtmixer + pedalboard (EQ/filter/effects)
- **Analysis**: librosa (BPM/key)
- **Stems/Upscale**: Demucs + AudioSR (HF)
- **MIDI/OSC**: mido + python-rtmidi + python-osc
- **GUI**: Dear PyGui (fast native decks/waveforms) or Tauri
- **Voice**: faster-whisper (tiny) + Ollama (small model)
- **Existing Sonic Forage**: autonomous-dj-os, starter-kit, prompt-arcade, safety gates

## Research & Resources (All Embedded)

- **Stable Audio 3** (May 2026): [stabilityai/stable-audio-3](https://github.com/Stability-AI/stable-audio-3) — small models CPU-friendly, variable length, inpainting/LoRA ready. Perfect for low-end machines.
- **Mixxx**: Gold-standard open-source DJ software. Community NS7II mappings exist. Great reference for UI/beatgrid/sync.
- **Numark NS7II**: High-res MIDI platters. Serato-native but fully mappable. Existing Mixxx XML mapping available.
- **AudioSR**: Versatile audio super-resolution to 48kHz.
- **Demucs**: Stem separation (drums/bass/vocals/other) for remixing.
- **Sonic Forage Ecosystem**: [github.com/Sonic-Forage](https://github.com/Sonic-Forage) — autonomous-dj-os, rave-harm-reduction, master-prompt-arcade, etc.

Full research notes in `docs/RESEARCH_SUMMARY.md`.

## Agentic Build Plan

This repo is laid out for agentic development. See `docs/AGENTIC_BUILD_PLAN.md` for phased tasks, each with clear prompts, acceptance criteria, and handoff points. Perfect for Grok, Claude, or other agents to execute step-by-step.

Phases:
1. Foundation & MVP Core (Decks + Gen + Mixer)
2. Hardware Integration & Polish
3. Autonomous Agent & Voice
4. Full Ecosystem Integration
5. Packaging, Docs, Launch

## Contributing & Culture

We follow Sonic Forage principles:
- Public-safe by default (harm-reduction prompts baked in)
- Closed gates for any outreach/booking (human approval only)
- Fork the signal, grow the scene
- No hype, only working experiments

See `docs/CONTRIBUTING.md` and `rave-harm-reduction-community-kit` in the org.

## License

Core code: MIT (or Stability AI Community License for model-related). Generated audio is yours.

**Let's forge the future of AI DJing.**

*Part of the Sonic Forage mycelium — https://github.com/Sonic-Forage*
