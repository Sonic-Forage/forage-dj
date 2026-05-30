# Research: DAW Frameworks, MIDI/OSC Controllers, Visualizers & Agentic Integration (May 2026)

This document captures autonomous research done for turning forage-dj into a full terminal + agentic DAW workstation with custom controllers, video sync, and realtime agent tools.

## 1. MIDI Controller Mapping (Custom Controllers + Learn Mode)

**Core Recommendation (still best in 2026):**
- `mido` + `python-rtmidi` (already our core deps) is the dominant, actively maintained choice.
- Higher-level frameworks worth evaluating:
  - **midi-scripter** — Excellent for filtering/routing/mapping + has GUI elements. Great for complex live controller setups.
  - **mdevtk** — Object-oriented device classes with callbacks for popular DJ controllers. Very clean for device-specific drivers + LED feedback.
  - **mididings** — Powerful DSL for MIDI routing/transforms (C++ speed, Python scripting). Excellent for live performance rules.

**Our Implementation (already done in this session):**
- `src/foragedj/hardware/midi.py` now has a proper `MidiMapper` with:
  - Dynamic `bind(param, "cc:0:7")` or note/pitch specs
  - Full `start_learn(param_name)` with automatic binding + persistence
  - Easy callback registration
  - Works with any controller (NS7II + generic)

This is production-ready for users to create their own mappings.

## 2. OSC & Video Integration (Resolume + Others)

**Resolume OSC (excellent for video sync):**
- Very well documented and discoverable (use "Edit OSC" mode in the UI — it literally shows the exact address for any control you click).
- Hierarchical and powerful: clips, layers, transport, effects, crossfader, BPM sync, etc.
- Normalized 0-1 values are standard. Good feedback support.
- Complements with a REST API + WebSockets if you need more.

**Our Implementation:**
- `src/foragedj/hardware/osc.py` now has a real `OSCBridge` using `python-osc`.
- Easy `.map(address, callback)` + `.send(address, value)`.
- Convenience factory for Resolume.
- CLI command: `foragedj osc-resolume`

**Poor Man's Visualizer:**
- We added `src/foragedj/visualizer.py` — a clean, modern Rich-based real-time waveform visualizer (inspired by current best terminal practices: sounddevice + numpy + rich Live).
- Can be driven by the same audio stream as the mixer.
- Easy to extend with spectrum, beat grid, etc.

**Future Integration Idea:**
Make the `live` autonomous mode automatically send BPM + energy + "next track starting" messages to Resolume via OSC so visuals react to the AI-generated set in real time.

## 3. DAW Frameworks & Path to Full Workstation

**Top Recommendation (2026): DawDreamer**
- Built on JUCE.
- VST2/3 hosting + parameter automation
- Faust DSP support (including JAX integration for ML/differentiable audio)
- Graph routing, Ableton-style warp markers, high-quality time-stretching
- Excellent for scriptable, reproducible DAW workflows and research.

**Strong Companion:**
- **Pedalboard** (Spotify) — already in our stack. Great for effects chains and VST loading. Works beautifully with NumPy/ML pipelines.

**Realtime / Creative Synthesis:**
- **pyo** — Mature C-backed Python module for low-latency realtime DSP, synthesis, effects, sequencing. One of the best options for building custom instruments or live performance tools in Python.

**Other Useful Pieces:**
- `dawproject-py` for session interchange with commercial DAWs.
- Existing stack we already rely on: librosa (analysis), sounddevice, mido, python-osc, pedalboard.

**Our Current Position + Roadmap:**
We already have a very strong foundation:
- Real-time mixer engine (sounddevice + pedalboard)
- Locked-seed generative setlists with rich analysis (BPM, key, Camelot, energy estimates, recommended transitions)
- Live autonomous mode with lookahead
- Flexible MIDI + OSC control layer
- Terminal-first philosophy + agentic design

**Next logical steps toward full DAW workstation (autonomous work ready):**
- Generalize mixer to N tracks + basic automation recording
- Add simple timeline / arrangement view (ASCII or rich)
- Integrate DawDreamer or pyo for plugin hosting + higher-quality time-stretching / warping
- Proper stem separation + per-stem mixing (we already have the `stems` extra)
- Recording + export of full sessions with embedded prompts/seeds
- Visual programming layer (Faust or node graph) for effects

## 4. Agentic Realtime API & Tools

For "CLI music and sample creator like agent realtime + all tools API":

The cleanest path is a small **FastAPI + WebSocket server** that exposes the entire system as tools:
- `/generate` (with manifest or free prompt + seed)
- `/live/start`, `/live/stop`, `/live/parameter`
- `/mixer/set` (volume, EQ, crossfader, etc.)
- `/load_library`
- `/trigger_resolume_clip` (via the OSC bridge)
- WebSocket for low-latency bidirectional control (perfect for agents)

This turns forage-dj into a first-class realtime tool server for Hermes-style agents or any other agent framework.

We already have the health/self-heal system as a great example of an agent-usable diagnostic tool.

## 5. Serato-like Analysis Enhancements (Already Strong Foundation)

We have:
- BPM + key detection (librosa)
- Camelot wheel compatibility
- Energy estimation in setlist manifests
- Recommended transitions with reasons

**Easy next wins:**
- Better phrase / section detection (using onset + energy curves)
- Harmonic mixing suggestions that also consider energy arc (we already started this in previous swarm work)
- Key detection improvements + confidence scores
- Automatic "harmonic setlist reordering" suggestion tool

## Conclusion & Recommendation

forage-dj is in an unusually good position:
- We have the generative AI layer (Stable Audio 3 + community LoRAs) working locally on Z:.
- We have strong analysis and reproducible setlist system.
- We now have proper MIDI + OSC control layers.
- We have the live autonomous "generate while playing" vision started.
- Everything is designed to be agentic and terminal-first.

The missing pieces for "full DAW workstation + much more" are mostly integration and polish on top of this excellent foundation, plus selective adoption of DawDreamer/pyo for heavier plugin/time-stretching needs.

This combination (generative + locked seeds + agentic control + terminal power + video sync) is genuinely unique and powerful.

All research and code above stays in the master repo on the Z: drive.

*Ready for the next autonomous push.* 🍓🎛️
