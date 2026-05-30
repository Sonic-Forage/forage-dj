# Architecture — forage-dj

**High-level system design for the AI DJ interface/DAW.**

## Core Principles
- Local-first (no cloud required for core features)
- Modular & forkable (every component replaceable)
- Real-time audio priority (low latency mixing > fancy visuals)
- Safety & culture embedded (Sonic Forage gates, harm-reduction prompts)
- Agent-friendly (clear interfaces, state machines, prompt contracts)

## High-Level Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        USER / HARDWARE                        │
│  (NS7II platters/faders/buttons, Touch OSC, Voice, GUI)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ MIDI / OSC / Keyboard
┌──────────────────────────────▼──────────────────────────────┐
│                     HARDWARE ABSTRACTION                     │
│  midi.py (mido/rtmidi + mapping + Learn) + osc.py            │
└──────────────────────────────┬──────────────────────────────┘
                               │ Control Events
┌──────────────────────────────▼──────────────────────────────┐
│                      DECKS & MIXER ENGINE                    │
│  Deck class (play/pause/position/volume/EQ/filter/pitch)     │
│  Mixer (rtmixer + sounddevice + pedalboard effects)          │
│  Analysis (librosa BPM/key/onset)                            │
└──────────────────────────────┬──────────────────────────────┘
                               │ Audio Buffers + State
┌──────────────────────────────▼──────────────────────────────┐
│                    AI GENERATION & POST-PROCESS              │
│  audio_gen.py (Stable Audio 3 wrapper + cache)               │
│  stems.py (Demucs) + upscale.py (AudioSR)                    │
│  prompt_engine.py (LLM for auto-mix decisions, voice intent) │
└──────────────────────────────┬──────────────────────────────┘
                               │ Generated WAVs + Metadata
┌──────────────────────────────▼──────────────────────────────┐
│                 AUTONOMOUS AGENT LAYER                       │
│  (Import from sonic-forage-autonomous-dj-os)                 │
│  Ralph loop, payload system, safety gates, persona           │
│  Auto-mix agent, setlist curator, voice responder            │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                           GUI / UI                           │
│  Dear PyGui (or Tauri) — Decks, waveforms, library,          │
│  prompt panels, status, voice visualizer                     │
└─────────────────────────────────────────────────────────────┘
```

## Key Modules (src/foragedj/)

- `audio_gen.py`: Stable Audio 3 calls, prompt formatting, duration handling, LoRA support.
- `mixer.py`: Core real-time engine. Deck dataclass + Mixer singleton.
- `hardware/`: midi.py, osc.py, mapping files (NS7II.json, learn_cache.json).
- `analysis.py`: librosa wrappers + key detection (Camelot helper).
- `voice.py`: STT + LLM intent → command router.
- `agent.py`: Thin wrapper around autonomous-dj-os + custom DJ logic.
- `gui/`: dearpygui_app.py (main window + widgets).
- `utils/`: config, logging, metadata (embed prompt + safety note in WAV).
- `stems.py` & `upscale.py`: Post-gen tools.

## Data Flow Example (Prompt → Mix)

1. User types "128bpm tech house, dark rave energy" in Deck 1 prompt.
2. `audio_gen.generate()` → calls SA3 small-music → saves `generated/2026-05-30_001.wav` + metadata.json.
3. Deck 1 loads WAV → analysis extracts BPM=128, key=Am.
4. User hits play or hardware play button → Mixer starts streaming Deck 1.
5. User adjusts filter on NS7II → MIDI event → Mixer applies pedalboard filter in real-time.
6. Voice: "auto mix" → voice.py parses → agent.py triggers transition logic → generate Deck 2 track with complementary prompt → crossfade.

## State Management
- Simple: JSON files or in-memory dicts for MVP (no heavy DB).
- Later: SQLite for library + set history.
- All generated tracks store: prompt, model, duration, BPM, key, safety_hash.

## Performance Targets
- Generation: <20s for 60s track on CPU (small model).
- Audio latency: <10ms round-trip for control changes.
- GUI: 60fps waveform updates.
- Memory: <2GB RAM baseline + model.

## Extensibility Points
- Swap GUI (Dear PyGui → web via FastAPI + nicegui).
- Swap mixer backend (rtmixer → Jack or WASAPI exclusive).
- Add new models via LoRA or future Stable Audio versions.
- Plug in different agent backends (Ollama, local Grok API, etc.).

*Designed for agents to implement one module at a time with clear interfaces.*
