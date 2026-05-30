# Agentic Build Plan for forage-dj

**This document is designed for AI agents (Grok, Claude, Cursor, etc.) to execute the build step-by-step.**

Each phase has:
- Clear objective
- Specific tasks with acceptance criteria
- Recommended tools / libraries
- Handoff notes for next phase
- Safety / culture gates (Sonic Forage style)

**Current Status**: Repo foundation complete. Start with Phase 0 if needed, then Phase 1.

---

## Phase 0: Repo Hygiene & Environment (1-2 hours)

**Objective**: Make the repo immediately cloneable and runnable by any agent or human.

**Tasks**:
1. Add `pyproject.toml` with dependencies (uv style, matching other Sonic-Forage repos).
2. Create `.gitignore` (models/, *.wav, venv/, etc.).
3. Add `src/foragedj/__init__.py` and basic package structure.
4. Create `scripts/setup.sh` or `install.py`.
5. Add GitHub Actions for basic lint/test (optional for MVP).
6. Update README with exact `uv sync` command once deps are set.

**Acceptance**: `uv sync` succeeds on fresh clone, `uv run foragedj --help` works (even if placeholder).

**Handoff**: Ready for core development.

---

## Phase 1: MVP Core — 2 Decks + Prompt Generation + Basic Mixer (3-5 days)

**Objective**: Working 2-deck interface where you type a prompt, generate audio with Stable Audio 3 small model, load into deck, and mix with basic controls.

**Tasks**:
1. **Audio Generation Module** (`src/foragedj/audio_gen.py`)
   - Integrate `stable-audio-3` lib (from Stability-AI/stable-audio-3).
   - Function: `generate_track(prompt: str, duration: int = 60, model: str = "small-music") -> Path`
   - Support small-music and small-sfx.
   - Add progress callback for Gradio-like or CLI feedback.
   - Cache generated files in `~/.foragedj/generated/`.

2. **Audio Engine** (`src/foragedj/mixer.py`)
   - Use `sounddevice` + `python-rtmixer` for low-latency playback.
   - Implement Deck class: play/pause, volume, pitch (basic), position.
   - 3-band EQ + low-pass/high-pass filter using `pedalboard`.
   - Crossfader with equal-power curve.
   - Simple beat-sync (use librosa BPM from generated file).

3. **GUI Foundation** (choose one — recommend Dear PyGui for speed)
   - Two deck panels with:
     - Prompt input + "Diffuse" button
     - Waveform (use pyqtgraph or matplotlib embedded, or simple canvas)
     - Transport (play/pause, cue, loop)
     - Volume fader, EQ knobs, filter
   - Master crossfader, BPM display, master volume.
   - Status bar: "Generating... 42%" etc.

4. **Basic Auto-Mix**
   - Button "Auto Mix" that:
     - Detects BPM/key of both decks (librosa)
     - Aligns beats
     - Crossfades over 8-16 bars
     - Simple rule-based or tiny LLM prompt for transition style.

**Acceptance Criteria**:
- User can generate 30-60s track from prompt in <30s on CPU (small model).
- Play two tracks simultaneously with smooth crossfade, no clicks.
- EQ/filter audible and responsive.
- Waveform updates in real time.
- No crashes on potato machine (8GB RAM, integrated GPU ok).

**Handoff**: Working local MVP. Next agent adds hardware + voice.

**Sonic Forage Gate**: All generated tracks include embedded metadata with prompt + safety note ("Public-safe rave tool — harm reduction first").

---

## Phase 2: Hardware Integration & Polish (2-3 days)

**Objective**: Full support for Numark NS7II + MIDI Learn + Touch OSC. Make it feel like a real DJ controller.

**Tasks**:
1. **MIDI Module** (`src/foragedj/hardware/midi.py`)
   - Use `mido` + `python-rtmidi`.
   - Auto-detect NS7II or generic controller.
   - Pre-load community mapping (convert existing Mixxx .midi.xml for NS7II to our control map).
   - MIDI Learn mode: click "Learn" then move control → assign to deck param.
   - Platters → scrub / jog wheel behavior.
   - Faders → volume/EQ/filter.
   - Buttons → cue, play, hotcue 1-4, effect on/off.

2. **OSC Support** (`src/foragedj/hardware/osc.py`)
   - python-osc for Touch OSC / mobile control.

3. **Polish**:
   - Add hotcue buttons in GUI.
   - Beat grid visualization (simple vertical lines on waveform).
   - Key detection + key match indicator (Camelot wheel simple version).
   - Recording: "Record Mix" button that exports WAV of master output.

**Acceptance**:
- NS7II platters control playback position smoothly.
- All main faders/knobs mapped and responsive (<10ms latency).
- MIDI Learn works end-to-end.
- Works on Linux/Mac/Windows (test matrix in CI later).

**Handoff**: Hardware-ready. Ready for autonomous agent layer.

---

## Phase 3: Autonomous Agent, Voice & Stems (3-4 days)

**Objective**: "Set it and forget it" mode + voice control + stem remixing.

**Tasks**:
1. **Voice Interface** (`src/foragedj/voice.py`)
   - `faster-whisper` tiny model for STT.
   - Local LLM (Ollama phi3:mini or gemma2:2b) for intent parsing.
   - Commands: "next track", "drop the bass", "add SFX pad [rain]", "auto mix on", "tell me a story" (fun mode).
   - Always-on hotword or push-to-talk button.

2. **Autonomous Agent** (integrate with `sonic-forage-autonomous-dj-os`)
   - Import Ralph loop / payload system.
   - Simple agent loop: analyze current mix → suggest/generate next track via prompt LLM → auto-load & transition.
   - Safety gate: human must approve any public posting or booking-related action.

3. **Stems & Post-Processing**
   - Demucs integration: button "Split Stems" on loaded track → 4 stems loadable to sampler pads.
   - AudioSR upscale on generated tracks (optional toggle for quality).

**Acceptance**:
- Voice command "generate house track 128bpm" works and loads deck.
- Auto-mix runs for 10+ minutes without intervention, musically coherent.
- Stems separate cleanly and can be mixed independently.

**Handoff**: Full single-user autonomous DJ experience.

---

## Phase 4: Ecosystem Integration & v0.5 (2-3 days)

**Objective**: Deep tie-in to Sonic Forage mycelium + 4-deck + library.

**Tasks**:
1. Load existing `sonic-forage-autonomous-dj-os` as submodule or import.
2. Add 4-deck layout (tab or side-by-side).
3. Library browser: list generated tracks, tag with prompts, search by vibe.
4. Sampler bank (8-16 pads) using small-sfx model.
5. Export setlist / mix recording with embedded prompts for provenance.
6. Add LoRA selector UI (list user fine-tunes).

**Acceptance**: User can run a full 1-hour autonomous set from voice commands only.

---

## Phase 5: Packaging, Docs, Launch Prep (2 days)

**Tasks**:
1. One-click installers (PyInstaller or briefcase for .exe/.app).
2. Comprehensive README + video demo script.
3. GitHub Releases with pre-built binaries.
4. Community kit: starter prompts, NS7II mapping files, safety prompt library.
5. Freemium hooks (placeholder for cloud API key).
6. Final culture review: all prompts reviewed for harm-reduction language.

**Launch Criteria**:
- `uv tool install foragedj` works.
- Demo video <3min showing prompt → mix → hardware control.
- Repo star-worthy (clean, documented, working).

---

## Agent Execution Tips

- Always run `uv sync` first in new environment.
- Use `uv run python -m foragedj` or similar.
- For GUI development, prefer Dear PyGui (fast iteration) over web unless Tauri requested.
- Test on CPU-only machine to ensure small models perform.
- Commit after each sub-task with clear message.
- If stuck on audio latency, profile with `py-spy` or sounddevice docs.
- Safety first: never remove the harm-reduction metadata or gates.

**Next Agent Prompt Example**:
"You are now the lead dev for Phase 1 of forage-dj. Start by reading docs/AGENTIC_BUILD_PLAN.md and docs/RESEARCH_SUMMARY.md. Implement the audio_gen.py and mixer.py modules first. Make the generate function work with Stable Audio 3 small model. Then build a minimal Dear PyGui with two decks. Push commits as you go."

---

*This plan is living — update it as we learn. Fork responsibly.*
