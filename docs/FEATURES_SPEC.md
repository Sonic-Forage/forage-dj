# Features Specification — forage-dj

**Detailed feature list with priorities, acceptance criteria, and Sonic Forage cultural notes.**

## P0 — MVP Core (Must have for first working demo)

### Deck System (2 decks)
- Prompt text input + "Diffuse / Generate" button per deck
- Generation status: progress bar + ETA (small model ~15-30s)
- Load generated or local WAV into deck
- Play/Pause, Cue (to start point), Loop (4/8/16 bars)
- Volume fader (0-100%)
- 3-band EQ (Low/Mid/High ±12dB) with visual knobs
- Filter (low-pass / high-pass, cutoff 20Hz-20kHz)
- Pitch bend / tempo adjust (±10%)
- Waveform display with playhead (simple scrolling or static with marker)
- BPM & Key display (auto-detected via librosa)

### Mixer
- Master crossfader (equal-power curve)
- Master volume + limiter
- Per-deck send to effects (future)
- Real-time metering (simple peak + RMS)

### Basic Auto-Mix
- One-button "Auto Mix" that:
  - Matches BPM (pitch one deck to match)
  - Aligns downbeat using onset detection
  - 8-16 bar crossfade with EQ ducking
  - Optional: LLM suggests transition style ("build tension", "drop hard")

### Generation Models
- Toggle: Music (small-music) / SFX (small-sfx) / Medium (if GPU)
- Duration slider 10-120s
- Prompt templates (from master-prompt-arcade): "dark techno 135bpm", "uplifting trance breakdown", etc.

## P1 — Hardware & Control (Next priority)

### Numark NS7II Support
- Full mapping out-of-box (platters, faders, buttons, touch FX)
- MIDI Learn: click any GUI control → move hardware control → auto-map
- Jog wheel behavior: scratch mode when paused, pitch bend when playing
- LED feedback where hardware supports (if any)
- Hotcue 1-4 per deck mapped to buttons

### Touch OSC / Mobile
- Basic layout: 2 decks + crossfader + master
- Send/receive OSC for wireless control

### Voice Commands (P1)
- Always-listening or push-to-talk
- Core commands: play/pause deck X, generate [prompt], auto mix, drop SFX [type], next track, record mix
- Fun commands: "tell me a rave story", "make it darker"
- Intent parsed by small local LLM → routed to actions

## P2 — Advanced DJ Features

- 4-deck layout (switchable or all visible on wide screens)
- Sampler bank (8 pads) — trigger SFX generated on-the-fly or from library
- Hotcue editor + visual markers on waveform
- Beat grid & quantize (snap loops/cues)
- Key matching visual (Camelot wheel mini)
- Effects rack (reverb, delay, glitch, filter sweep) with chain
- Stem separation button → 4 stems appear as sub-decks or pads
- AudioSR upscale toggle (quality vs speed)
- Mix recording (master output to WAV + JSON setlist with prompts)

## P3 — Autonomous & Ecosystem

- Full Ralph loop integration from autonomous-dj-os
- Autonomous set mode: "Play 60min set in [genre]" → AI curates prompts, generates, mixes, transitions
- Library: searchable, tagged, prompt-history, favorite generations
- LoRA manager: list/train/apply user style models
- Community vault sync (opt-in, with safety review)
- Export "set package" (all tracks + prompts + metadata) for sharing

## Non-Functional Requirements

- Latency: Control changes <10ms audible latency
- Generation: 60s track <25s on CPU-only (Ryzen 5 / M1 equivalent)
- Stability: No crashes during 2hr continuous mix
- Accessibility: High contrast mode, keyboard navigation, screen reader friendly (future)
- Size: Installer <500MB (models cached separately)

## Sonic Forage Cultural Features (Non-Negotiable)

- Every generated track embeds metadata: original prompt, model version, generation timestamp, safety_note="This tool is for personal/creative use. Practice harm reduction."
- Auto-mix agent includes harm-reduction context in prompts ("keep the energy positive and inclusive")
- No autonomous posting or booking actions without explicit human gate (from autonomous-dj-os)
- All prompts default to public-safe language; user can override but gets warning
- Rave glossary / harm-reduction quick reference accessible from menu

**This spec evolves with user feedback. Prioritize working music over perfect UI.**
