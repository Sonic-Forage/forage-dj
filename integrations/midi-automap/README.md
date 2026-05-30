# MIDI Auto-Mapping & Realtime Adaptation

**Feature Request**: "Auto map where it takes your devices, tests all the keys and determines best mapping and we can change/adapt realtime."

## Plan

- Extend existing `src/foragedj/hardware/midi.py` (which already has good learn mode)
- Add "Auto Discover" mode:
  1. User plugs in controller
  2. System sends test notes/CCs
  3. Records responses + latency
  4. Builds optimal mapping (volume, play/pause, region select, prompt queue, etc.)
  5. Saves profile
- Realtime adaptation: During performance, system can suggest or auto-remap based on usage patterns or errors

## Files to Create

- `src/foragedj/hardware/midi_automap.py`
- Profiles stored in `sessions/<name>/midi_profiles/`

This is huge for workshops, clubs, raves, and "plug and play" autonomous installs in new venues.

All development stays inside the project root.
