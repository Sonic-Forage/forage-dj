# Sonic Forage Media Player — Feature Vision & Roadmap

**Context**: The project is evolving from a generative tool + basic mixer into a full **AI-native Music Workstation + Media Player** that feels like a terminal-first Ableton + Serato hybrid, with deep generative editing capabilities.

This document captures what a "bad ass" media player experience needs to feel complete and professional for live performance, editing, streaming, and autonomous deployment.

## Current State (as of late May 2026)

**Strengths**:
- Real-time 2-deck mixer (`mixer.py`) with pedalboard effects
- Excellent terminal waveform visualizer (`visualizer.py`)
- Strong region/arrangement data model in `workstation.py` with beautiful Rich timeline
- Deep analysis (BPM, key, Camelot, onsets)
- Good foundation for low-latency potato-machine use

**Major Gaps for a Real Media Player**:
- No proper region-level playback (you can edit regions but can't easily play just a region or an arrangement)
- Weak transport controls (seek, loop, hotcues, nudge)
- No multi-track / full arrangement playback engine
- Limited stem support in the player
- No recording or clean bounce/export of edited sessions
- Playback is not well integrated with the workstation editing workflow
- No "performance mode" vs "editing mode" differentiation

## Core Media Player Features We Need

### Tier 1 — Must Have Soon (Makes it actually usable as a player)

1. **Region & Arrangement Playback**
   - Play any single region from a workstation session
   - Play full tracks with region boundaries respected
   - Play entire arrangements/sessions in correct time order with automatic crossfades

2. **Proper Transport Controls**
   - Play / Pause / Stop
   - Seek (by time or by beat)
   - Loop a region or selection
   - Hotcues / cue points per track or region (MIDI mappable)
   - Nudge / pitch bend during playback

3. **Stem Playback**
   - When stems exist (from `split-stems`), allow playing individual stems or mute/solo them during playback
   - Critical for live remixing and the "edit while playing" workflow

4. **Waveform + Timeline Interaction**
   - Make the existing Rich visualizer more interactive (keyboard navigation of regions)
   - Visual playhead in the arrangement view
   - Click-to-seek approximation (even if just keyboard-driven at first)

5. **Recording & Export**
   - Record the output of a performance (including live edits)
   - Bounce an edited session/arrangement to a new master WAV (with proper metadata via `tag-library`)
   - This feeds directly into Swarm Distribution + seed bombing

### Tier 2 — Makes it Feel Professional

6. **Performance vs Editing Modes**
   - Low-latency "live" mode (smaller buffers, lighter effects)
   - High-quality "production" mode for critical listening / final bounces

7. **Per-Region / Per-Track Effects**
   - Non-destructive effects that can be toggled or automated per region
   - Saved in the session file

8. **Better Library / Crate Experience**
   - Terminal-based music library browser (search, filter by key/BPM/energy, quick preview)
   - Drag regions between sessions (in the data model + UI)

9. **Reactive Visuals During Playback**
   - Drive Avaturn characters from real-time playback position + audio features
   - Big visual feedback in the retro OS when playing

10. **Robust Audio Device Handling**
    - Easy device selection
    - Auto-reconnect on device change (important for different venues on tour)
    - Virtual output routing helpers for OBS/streaming

### Tier 3 — Differentiators (The "AI Workstation" Magic)

11. **Live Generative Playback**
    - While playing a region, the system can be generating the *next* region in the background based on current energy / chat / analysis
    - Seamless handoff when the current region ends

12. **AI-Assisted Mixing**
    - Automatic EQ / level suggestions based on key compatibility and energy
    - "Smart crossfade" suggestions between regions

13. **Multi-User / Remote Playback**
    - Multiple people controlling different aspects of the same arrangement during a performance or workshop

## Integration Priorities

The media player must integrate tightly with:

- **Workstation** — Editing and playback should feel like one continuous experience
- **Swarm Distribution** — Easy export of performed/edited material + automatic seed bombing
- **Event/Tour System** — Reliable playback during long harm-reduction events
- **Docker Autonomous Deployment** — The player needs to be scheduleable and headless-friendly
- **Retro OS** — A first-class "Media Player" chunky app with big readable transport
- **MIDI Auto-Map** — Full transport mapping (play, cue, loop, region select, etc.)
- **Avaturn** — Characters that visibly react to what's currently playing

## Suggested Implementation Order (Autonomous-Friendly)

**Phase A (High leverage, relatively contained)**
- Extend `mixer.py` or create `player.py` with region playback  ← **Started May 2026**
- Add basic transport (play/pause/seek/loop) exposed in CLI and workstation
- Make the Rich arrangement view show a live playhead during playback

**Progress**: `src/foragedj/player.py` created with `MediaPlayer` class + region playback foundation. CLI commands `play-region` and `player-stop` added. Retro OS now has a "▶️ Media Player" chunky button.

**Phase B**
- Stem mute/solo support
- Recording + bounce functionality
- Hotcues / cue points

**Phase C**
- Performance vs Editing mode switching
- Better library browser in the retro OS
- Tight Avaturn + reactive visuals during playback

**Phase D**
- Live generative continuation while playing
- Advanced AI mixing assistance

## Non-Technical "Stuff" We Probably Also Need

- Clear "Performance Rider" section in the event docs (what audio interface, monitors, power, etc. are recommended)
- Training materials for using the media player in a live harm-reduction context
- Example MIDI mapping profiles for common controllers (pioneer, akai, etc.) generated by the auto-map tool
- OBS-friendly "big transport" view (large BPM, current region name, remaining time)

---

This media player is one of the last big missing pieces that will make the whole system feel like a *complete* tool you can actually take on tour or install at a club.

Once we have solid region playback + transport + export, the combination of:
- Generative power (workstation + swarm)
- Live editable performance (media player)
- Autonomous scheduling (Docker)
- Cultural positioning (rave-prep, harm reduction events)

...becomes extremely compelling.

Let's build the player.
