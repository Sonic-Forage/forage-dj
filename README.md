# forage-dj

**Sonic Forage DJ** — Open-source AI-powered autonomous DJ interface & DAW

**Prompt-to-track generation • Setlist-as-Score with Seed Variation • Stable Audio 3 • Numark NS7II MIDI • Real-time mixing • Auto-mix agent • Voice commands**

[![License: Community](https://img.shields.io/badge/License-Stability%20AI%20Community-blue)](https://stability.ai/license)

> **New:** Full White Paper published — [docs/WHITEPAPER.md](docs/WHITEPAPER.md) — detailing the "setlist as prompt score + seed variation" innovation, differentiation from real-time engines like Daydream DEMON, and full vision for accessible AI DJing.

## Vision

ForageDJ turns any computer (even potato machines) into a full autonomous DJ rig. Generate tracks on-the-fly or from setlists of prompts, mix live with hardware like the Numark NS7II, and embrace the stochastic magic of AI: **one setlist of prompts + one seed = one unique performance; change the seed = an entirely new sonic experience while keeping the same structure and energy arc.**

This is **not** a real-time continuous diffusion live engine (see Daydream DEMON for that). This is a simple, powerful **generate + mix DAW** with agentic setlist curation, hardware control, and infinite replayability through seed variation. Perfect for home producers, rave organizers, and performers who want prompt-driven music without constant model streaming.

Built on the Sonic Forage mycelium: safety gates, harm-reduction prompts, Ralph loop from autonomous-dj-os, and public-safe defaults.

**Fork it. Change the seed. Play it different every time.**

## Quick Start (MVP Foundation)

```bash
# Clone
 git clone https://github.com/Sonic-Forage/forage-dj.git
 cd forage-dj

# Setup (uv recommended)
 uv sync --extra cpu   # or --extra cuda

# Run (placeholder — see AGENTIC_BUILD_PLAN.md for Phase 1)
 uv run foragedj
```

**Status**: White paper + full research + agentic plan complete. Phase 1 (2-deck + gen + mixer + seed control) ready for implementation.

## Core Innovation: Setlist as Prompt Score + Seed Variation

- Write a setlist as a list of prompts (e.g., dark techno intro, uplifting breakdown, hard drop with SFX).
- Generate the full set with seed=42 → coherent 60-min DJ experience with matching BPMs/transitions.
- Re-generate with seed=1337 → completely different realizations (melodies, textures, SFX) but same energy curve and structure.
- Infinite unique mixes from one "score" (the prompt list). Share setlist recipes; everyone gets their own version.
- Embraces diffusion stochasticity as a feature, not a bug — turns prompt engineering into a new compositional practice.

See WHITEPAPER.md for formal treatment and comparison to real-time tools.

## Key Features (Roadmap)

### MVP (v0.1 - Phase 1)
- 2 decks with prompt input + "Diffuse" (Stable Audio 3 small-music/sfx) + seed control
- Real-time mixer: volume, 3-band EQ, filter, crossfader (sounddevice + pedalboard)
- Basic setlist runner (generate all prompts sequentially, auto crossfades)
- Waveform + BPM/key (librosa)
- Numark NS7II MIDI mapping + Learn (community mappings ported)

### v0.5 (Phases 2-3)
- Voice commands + autonomous agent (Ralph loop)
- Stem separation (Demucs) + SFX pads
- Full setlist editor (drag-drop prompts, per-item seed, preview)
- 4-deck + sampler + hotcues

### v1.0+
- LoRA fine-tuning UI
- Community setlist vault (safety-reviewed)
- One-click installers + freemium cloud options

## Tech Stack

- **Python 3.12 + uv** (pyproject.toml ready)
- **Generation**: stabilityai/stable-audio-3 (small models CPU-friendly, seed support)
- **Mixing**: sounddevice + python-rtmixer + pedalboard
- **Analysis**: librosa
- **Hardware**: mido + python-rtmidi (NS7II preset + Learn)
- **Voice**: faster-whisper + Ollama small LLM
- **Stems/Upscale**: Demucs + AudioSR
- **GUI**: Dear PyGui (fast native)
- **Agent Layer**: sonic-forage-autonomous-dj-os (Ralph loop, safety gates)

## Research & Resources

Full details in `docs/RESEARCH_SUMMARY.md` and `docs/WHITEPAPER.md`.
- Stable Audio 3 (May 2026): CPU small models, variable length, LoRA/editing.
- Daydream DEMON (2026): Real-time 25Hz diffusion — we differentiate by focusing on batch + mix + setlist scores.
- Mixxx + NS7II mappings, AudioSR, Demucs, CHI 2026 live music agents paper, ProGress structured diffusion, etc.

## Agentic Build Plan

See `docs/AGENTIC_BUILD_PLAN.md` — 5 phases with tasks, acceptance criteria, and example prompts for other agents. White paper + setlist innovation integrated into Phase 1+ priorities.

## Contributing & Culture

Sonic Forage principles: public-safe defaults, closed gates for autonomous actions, harm-reduction baked in (every track embeds safety note + prompt provenance), fork the signal, grow the scene.

See `docs/CONTRIBUTING.md` (to be added) and org repos for rave-harm-reduction kit.

## License

Core: MIT / Stability AI Community. Generated audio yours. Prompts/sets shareable.

**Let's forge infinite AI DJ experiences — one prompt list, endless seeds.**

*Part of the Sonic Forage mycelium — https://github.com/Sonic-Forage*
