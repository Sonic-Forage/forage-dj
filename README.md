# forage-dj

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

## Quick Start (Environment Fixed — Phase 0 Complete)

```bash
# Clone
git clone https://github.com/Sonic-Forage/forage-dj.git
cd forage-dj

# One-shot setup — works on Linux + Windows (recommended)
python scripts/install.py
# or
python scripts/install.py --full

# Legacy convenience (still works)
# ./scripts/setup.sh          (Linux/mac)
# powershell -File scripts/setup.ps1   (Windows)

# Verify everything (run this first on any machine)
uv run foragedj doctor

# Play with the CLI immediately
uv run foragedj --help
uv run foragedj generate "dark techno 128bpm" --seed 42 --dry
```

**⚠️ Model Access Required (Gated HF Repos)**: Stability Audio 3 models need one-time license acceptance + HF_TOKEN.  
See **[docs/MODEL_ACCESS.md](docs/MODEL_ACCESS.md)** and **[docs/INSTALL.md](docs/INSTALL.md)** for the exact steps + the recommended **potato machine offline workflow** using `scripts/download_checkpoints.py` + large-drive caching (cross-platform helpers in `.grok/hf-cache.env` + `.grok/hf-cache.ps1`).

**Current Status** (May 2026):
- ✅ Full models + all Sonic-Forage LoRAs downloaded locally on Z:
- ✅ `foragedj download-models`, `generate-setlist`, `live`, `doctor --heal` all wired
- ✅ **NEW**: `uv run python -m foragedj.os` — Boot the full retro Music Diffusion Operating System (old-school terminal desktop UI)
- Active autonomous development toward full DAW workstation + realtime agentic AI tools + custom MIDI/OSC controllers + video sync

**Streaming & Going Live**

The workstation is designed for real performances. See:
- `docs/LIVE_STREAMING_GUIDE.md`
- `docs/LAUNCH_AND_STREAMING_STRATEGY.md`
- `uv run foragedj stream-prep --obs --twitch`

**Try the OS interface right now:**
```bash
uv run python -m foragedj.os
```

Logos live in `assets/logos/` (main root on Z: drive).

### Deploy on RunPod (Cloud GPUs)

See the full guide: `docs/RUNPOD_DEPLOYMENT.md`

Quick start:
- Use a Network Volume for `checkpoints/` + libraries (models are large).
- Follow the manual steps or use the skill in `skills/runpod-forage-dj/SKILL.md` with any compatible AI agent.
- Future: `python scripts/runpod_deploy.py` will take your `RUNPOD_API_KEY` and boot a fully configured pod.

See `docs/MISSION_GUIDE.md`, `docs/TERMINAL_DJ_IDE.md`, `docs/RESEARCH_DAW_CONTROLLERS_VISUALIZERS.md`, and `skills/runpod-forage-dj/SKILL.md`.
- Full whitepaper, architecture, agentic build plan, NS7II mapping research, and testing guides ready for contributors

See `docs/AGENTIC_BUILD_PLAN.md` and `agent/AGENT_START_HERE.md` to claim swarm tasks.

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

Full notes: [RESEARCH_SUMMARY.md](docs/RESEARCH_SUMMARY.md) | [MODEL_ACCESS.md](docs/MODEL_ACCESS.md) | [WHITEPAPER.md](docs/WHITEPAPER.md) | [ARCHITECTURE.md](docs/ARCHITECTURE.md)

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
