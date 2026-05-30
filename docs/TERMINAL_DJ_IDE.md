# forage-dj — Terminal DJ IDE + Live Autonomous DJ Vision

**Goal**: Turn forage-dj into a full-featured, keyboard-driven, agentic **DJ IDE** that feels as powerful as Serato or VirtualDJ, but lives entirely in the terminal (with optional GUI).

Inspired by (but not copying):
- **Mixxx** (open architecture, Control bus, Auto DJ, analysis, controller mappings)
- **djcmd** (real ncurses TUI DJ with decks, ASCII waveforms, hotcues, sync)
- Winamp (playlist energy + simplicity)
- Modern TUI tools (ratatui, textual, btop-style interfaces)

## Core Philosophy

- **Everything in the terminal first** (ASCII / rich TUI)
- **Agentic & autonomous by default** — multiple agents can collaborate in realtime
- **Generate while you play** (the killer feature)
- **Locked seeds + manifests** for reproducible, shareable sets
- **Potato machine friendly** (small models + smart lookahead)
- **Professional DJ workflow** (decks, EQ, crossfader, hotcues, sync, waveforms) without the bloat

## The "DJ IDE" Experience

Imagine opening a terminal and having:

- Multiple "decks" as panes or tabs
- Live waveform / beat grid visualization (ASCII or rich blocks)
- Full mixer (3-band EQ, filter, crossfader, master)
- Hotcues, loops, performance pads (keyboard-driven)
- Library browser with BPM/Key/Camelot search
- **Autonomous generation** happening in the background while you mix

### Live Autonomous DJ Mode (The Dream)

```bash
foragedj live --manifest setlists/my_festival_set.yaml --lookahead 2
```

Behavior:
- Starts playing track 1
- While track 1 plays → generates track 2 (and optionally track 3)
- When track 1 is near end → seamless crossfade into track 2
- Agent can suggest next tracks, adjust energy, or even generate new variations on the fly
- Settings:
  - `--lookahead 1` or `2` (recommended for most machines)
  - `--realtime` (attempt true realtime generation if your GPU/CPU is strong enough)
  - `--model small-music` (for speed) or `medium`

This turns the entire system into a **live co-pilot** rather than just a generator.

## Architecture Inspiration (Adapt, Don't Copy)

From Mixxx:
- Central "Control" system (pub/sub for all parameters) → perfect for CLI REPL + agents
- Strict separation of realtime audio engine from UI/analysis
- Worker threads for loading + analysis

From djcmd:
- ncurses TUI with decks on top, browser below
- Scrolling 3-band ASCII waveforms (red/green/blue)
- Hotcues, loops, sync indicators
- MIDI learn + mappings

From Winamp:
- Simple, beloved playlist experience
- "Generate full set → come back to a ready-to-play library"

## Current State (as of now)

- Strong foundation: `generate-setlist` (walkaway), rich `library.json` + `playlist.txt`
- Basic real-time mixer (`sounddevice` + `pedalboard`)
- `play-library` command (Winamp-style metadata viewer)
- New: `live` command (autonomous DJ with lookahead)
- Basic config system (`src/foragedj/config.py`)
- Locked seed manifests
- Good analysis (BPM, key, Camelot compatibility)

## Next Steps (Autonomous Work in Progress)

- [ ] Full TUI mixer with ASCII decks + waveforms (using `textual` or rich + prompt_toolkit)
- [ ] Improve `live` mode with real background generation + seamless crossfades
- [ ] Richer config (lookahead, realtime, model per energy level)
- [ ] Agent skills / tools for Hermes-style agents to control live mixing
- [ ] Better terminal visualizations (beat grids, phase meters, energy arcs)
- [ ] Hotcues + loops in the TUI player
- [ ] MIDI controller support in the terminal mixer

## Why This Matters

Most "AI music" tools are either:
- One-shot generators (no live performance)
- Real-time diffusion monsters (require beefy GPU, hard on potato machines)

forage-dj aims to be the **missing middle**:
- Professional DJ workflow
- Agentic automation
- Works great on modest hardware
- Reproducible + shareable via manifests + seeds
- Lives in the terminal (hackable, scriptable, agent-friendly)

This is the future of rave tooling.

---

*Fork it. Build the terminal. Play it different every time.*
