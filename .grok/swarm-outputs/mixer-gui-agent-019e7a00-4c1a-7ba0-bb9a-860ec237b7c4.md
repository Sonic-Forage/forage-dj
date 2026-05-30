# Swarm Agent Output: Phase 1 Mixer + Minimal GUI

**Subagent ID**: 019e7a00-4c1a-7ba0-bb9a-860ec237b7c4
**Type**: general-purpose
**Task**: Phase 1 Mixer + minimal GUI swarm agent - latency architecture + code skeletons
**Duration**: 99.93s | Tool calls: 26

---

## Key Deliverables

### 1. Real-time Architecture (sounddevice + pedalboard + numpy)
- Detailed design for low-latency callback (<10-15ms target).
- Uses fixed 44100 SR, float32 stereo.
- Per-deck Pedalboard for EQ + filter (mutable in place).
- Equal-power crossfade math.
- Pitch via interpolation.
- No locks in hot path.

### 2. 20-line _audio_callback skeleton (ready to drop in)
See the agent's output for the exact code block.

Supporting changes needed:
- Add imports for sounddevice + specific pedalboard classes.
- Extend `load_deck` to load audio buffers + build boards.
- Add `start()` / `stop()` methods.
- Add `_get_or_build_board(d)` helper.

### 3. Minimal Viable Dear PyGui 2-Deck Layout
- Side-by-side decks with prompt + Diffuse button.
- Transport, 5 controls per deck (volume, 3-band EQ, filter).
- Crossfader, master, status.
- Wiring pattern using dpg callbacks + timer for state polling.
- Direct integration with existing `Mixer` and `audio_gen.generate_track(..., progress_callback=...)`.

### 4. Ubuntu 24.04 Audio Gotchas
- Critical: `libportaudio2` must be installed at runtime (setup.sh does this).
- PipeWire vs ALSA/JACK latency notes.
- `foragedj doctor` already surfaces device issues.

**Status**: GUI/MIXER SKELETON READY

Full raw details in the original subagent output (tool history).
