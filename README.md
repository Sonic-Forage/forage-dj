# forage-dj

<p align="center">
  <img src="https://raw.githubusercontent.com/Sonic-Forage/forage-dj/main/assets/foragedj-logo.png" alt="ForageDJ Logo" width="400"/>
</p>

<h1 align="center">FORAGEDJ</h1>
<p align="center">
  <strong>Sonic Forage DJ</strong> — Open-source AI-powered autonomous DJ interface & DAW<br/>
  <em>One Prompt. Infinite Sets.</em>
</p>

<p align="center">
  <a href="https://github.com/Sonic-Forage/forage-dj/issues"><img src="https://img.shields.io/github/issues/Sonic-Forage/forage-dj?style=for-the-badge&color=ff00aa" alt="Issues"/></a>
  <a href="https://github.com/Sonic-Forage/forage-dj"><img src="https://img.shields.io/github/stars/Sonic-Forage/forage-dj?style=for-the-badge&color=00ff9f" alt="Stars"/></a>
  <a href="https://github.com/Sonic-Forage/forage-dj/blob/main/docs/WHITEPAPER.md"><img src="https://img.shields.io/badge/White%20Paper-Read%20Now-9d4edd?style=for-the-badge" alt="White Paper"/></a>
  <a href="https://stability.ai/license"><img src="https://img.shields.io/badge/License-Stability%20AI%20Community-blue?style=for-the-badge" alt="License"/></a>
</p>

---

**Prompt-to-track generation • Setlist-as-Score with Seed Variation • Stable Audio 3 • Numark NS7II MIDI • Real-time mixing • Auto-mix agent • Voice commands**

> **🚀 Swarm Active:** 4 parallel agent tasks open — [claim one here](https://github.com/Sonic-Forage/forage-dj/issues?q=is%3Aissue+label%3Aswarm)

## Vision

ForageDJ turns any computer (even a potato machine) into a full autonomous DJ rig. Generate tracks on-the-fly or from **setlists of prompts**, mix live with hardware like the Numark NS7II, and embrace the stochastic magic of AI:

**One setlist of prompts + one seed = one unique performance.**
**Change the seed = an entirely new sonic experience** while keeping the same structure, energy arc, and transitions.

This is **not** a real-time continuous diffusion live engine (check Daydream DEMON for that vibe). This is a simple, powerful **generate + mix DAW** with agentic setlist curation, hardware control, and infinite replayability. Perfect for home producers, rave organizers, and performers who want prompt-driven music without constant model streaming.

Built on the Sonic Forage mycelium: safety gates, harm-reduction prompts, Ralph loop from autonomous-dj-os, and public-safe defaults.

**Fork it. Change the seed. Play it different every time.** 🍓🎛️

## Quick Start (MVP Foundation)

```bash
# Clone
 git clone https://github.com/Sonic-Forage/forage-dj.git
 cd forage-dj

# Setup (uv recommended - matches your other Sonic-Forage repos)
 uv sync --extra cpu   # or --extra cuda for GPU

# Run (placeholder — full MVP coming via swarm)
 uv run foragedj
```

**Current Status**: White paper + full research + agentic plan + badass logo complete. Phase 1 (2-deck + gen + mixer + seed control) in active swarm development.

## Core Innovation: Setlist as Prompt Score + Seed Variation

- Write a setlist as a list of prompts (e.g. "dark techno intro 128bpm", "uplifting breakdown", "hard drop with SFX").
- Generate the full set with `seed=42` → coherent 60-min DJ experience with matching BPMs/transitions.
- Re-generate with `seed=1337` → completely different realizations (melodies, textures, SFX) but same energy curve and structure.
- Infinite unique mixes from one "score" (the prompt list). Share setlist recipes; everyone gets their own version.
- Embraces diffusion stochasticity as a feature — turns prompt engineering into a new compositional practice.

📖 See the full [WHITEPAPER.md](docs/WHITEPAPER.md) for the formal treatment, Daydream differentiation, and architecture.

## Key Features (Roadmap)

### MVP (v0.1 — Phase 1, Swarm Active)
- 2 decks with prompt input + "Diffuse" button (Stable Audio 3 small-music/sfx) + seed control
- Real-time mixer: volume, 3-band EQ, filter, crossfader (sounddevice + pedalboard)
- Basic setlist runner (generate all prompts sequentially with shared/per-item seeds, auto crossfades)
- Waveform + BPM/key detection (librosa)
- Numark NS7II MIDI mapping + MIDI Learn (community mappings ported)

### v0.5 (Phases 2-3)
- Voice commands + autonomous agent (Ralph loop integration)
- Stem separation (Demucs) + SFX pads from small-sfx model
- Full setlist editor (drag-drop prompts, per-item seed/transition, live preview)
- 4-deck + sampler + hotcues + beat grid

### v1.0+
- LoRA fine-tuning UI + style personalization
- Community setlist vault (safety-reviewed prompts)
- One-click installers (.exe/.app) + optional freemium cloud acceleration

## Tech Stack

- **Python 3.12 + uv** (pyproject.toml ready, matches your ecosystem)
- **Generation**: `stabilityai/stable-audio-3` (small models CPU-friendly, native seed support)
- **Mixing Engine**: `sounddevice` + `python-rtmixer` + `pedalboard` (EQ/filter/effects, low latency)
- **Analysis**: `librosa` (BPM, key, onset)
- **Hardware**: `mido` + `python-rtmidi` (NS7II preset + full Learn mode)
- **Voice**: `faster-whisper` (tiny) + Ollama small LLM
- **Stems/Upscale**: Demucs + AudioSR
- **GUI**: Dear PyGui (fast native decks/waveforms)
- **Agent Layer**: `sonic-forage-autonomous-dj-os` (Ralph loop, payloads, safety gates)

## Research & Resources

Everything verified and embedded:
- **Stable Audio 3** (May 2026) — CPU small models, variable length, LoRA/editing/inpainting.
- **Daydream DEMON** (2026) — Real-time 25Hz diffusion (we differentiate: batch + mix + setlist scores for accessibility).
- Mixxx + existing NS7II mappings, AudioSR, Demucs, CHI 2026 live music agents paper, ProGress structured diffusion, Sony LLM2Fx-Tools, responsible AI reviews.

Full notes: [RESEARCH_SUMMARY.md](docs/RESEARCH_SUMMARY.md) | [WHITEPAPER.md](docs/WHITEPAPER.md) | [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Agentic Build Plan & Swarm

See [AGENTIC_BUILD_PLAN.md](docs/AGENTIC_BUILD_PLAN.md) — 5 phases with tasks, acceptance criteria, and ready-to-copy prompts for other agents.

**Current Swarm Tasks (claim one!):**
- [Phase 1: Audio Gen + Seed Control](https://github.com/Sonic-Forage/forage-dj/issues/1)
- [Phase 1: Mixer + 2-Deck GUI](https://github.com/Sonic-Forage/forage-dj/issues/2)
- [Phase 2: NS7II MIDI + Voice](https://github.com/Sonic-Forage/forage-dj/issues/3)
- [Phase 3: Setlist Editor + Autonomous Agent](https://github.com/Sonic-Forage/forage-dj/issues/4)

## Contributing & Culture

We follow Sonic Forage principles:
- Public-safe by default (harm-reduction prompts baked in)
- Closed gates for any autonomous outreach/booking (human approval only)
- Every generated track embeds safety note + prompt provenance
- Fork the signal, grow the scene
- No hype — only working experiments

See org repos for `rave-harm-reduction-community-kit` and `sonic-forage-master-prompt-arcade`.

## License

Core code: MIT (or Stability AI Community License for model-related parts). Generated audio is 100% yours. Setlist recipes are meant to be shared and remixed.

---

**Let's forge infinite AI DJ experiences — one prompt list, endless seeds.** 🍓🔥

*Part of the Sonic Forage mycelium — https://github.com/Sonic-Forage*
