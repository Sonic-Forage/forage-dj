# Numark NS7II Hardware Integration Guide — forage-dj

**Detailed mapping, setup, troubleshooting, and MIDI Learn instructions.**

## Controller Overview

- **Platters**: 2x high-resolution jog wheels (vinyl mode feel). Great for scratching, pitch bending, scrubbing.
- **Faders**: Channel faders + crossfader + EQ (high/mid/low per channel in Serato mode, but we map freely).
- **Buttons**: Play, Cue, Hotcue 1-4, Loop, Effects, Touch FX, etc.
- **MIDI**: High-res (14-bit where supported), low latency USB.
- **Native**: Designed for Serato DJ (full feature unlock). We treat it as generic high-end MIDI controller.

## Recommended Mapping (Out-of-Box)

**Deck 1 (Left)**:
- Platter: Jog / Scrub (MIDI CC or note)
- Channel Fader: Deck 1 Volume
- EQ High/Mid/Low: Deck 1 EQ knobs
- Filter: Dedicated filter knob or assign one
- Play: Button → Deck 1 Play/Pause
- Cue: Button → Deck 1 Cue
- Hotcue 1-4: Buttons → Set / Jump to hotcues

**Deck 2 (Right)**: Symmetric mapping.

**Master**:
- Crossfader: Master crossfader
- Master Volume: Master fader (if present) or assign

**Global**:
- Effect buttons: Toggle effects rack or specific FX (reverb, delay)
- Touch FX: Momentary filter sweep or glitch

## How to Load the Mapping

1. Run `foragedj` with `--midi-learn` or open Settings → MIDI.
2. Select "Numark NS7II" preset (we will ship JSON mapping file).
3. If not perfect, use MIDI Learn mode.

## MIDI Learn Flow (in App)

1. Click "Learn" next to any control (e.g. Deck 1 Volume).
2. Move the physical fader/platter/button on NS7II.
3. App captures MIDI message (CC/note + channel + value range).
4. Saves to `~/.foragedj/midi_mappings.json`.
5. Persists across sessions.

**Example mapping JSON** (will be generated):
```json
{
  "deck1_volume": {"type": "cc", "channel": 0, "control": 7, "min": 0, "max": 127},
  "deck1_platter": {"type": "cc", "channel": 0, "control": 48, "mode": "jog"},
  ...
}
```

## Existing Community Resources

- Mixxx NS7II mapping: https://mixxx.discourse.group/t/numark-ns7-ii-mapping-numark-ns7-2/24674
  - Download their .midi.xml and we can auto-convert or manually port key controls.
- Serato mapping files (if user has backup).

## Troubleshooting

- **No MIDI input**: Check `lsusb` / Device Manager, install any Numark drivers (rarely needed on modern OS).
- **Platters not smooth**: Use high-res 14-bit CC if available; fall back to 7-bit with acceleration curve.
- **Latency**: Use low buffer size in sounddevice (64-128 samples).
- **Windows**: ASIO driver recommended for audio + MIDI combo.

## Future: Advanced Features
- Motorized fader feedback (if hardware supports in future models).
- Haptic / LED sync with beat grid.
- Multi-controller (NS7II + additional pads).

**This controller turns forage-dj from "software" into a real instrument.**
