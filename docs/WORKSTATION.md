# Sonic Forage Workstation — The Bad-Ass Ableton Killer

**"Diffusion-powered DAW that feels like Ableton on steroids, but lives entirely on your mounted drive and has a soul."**

## Vision

forage-dj is evolving from an autonomous generative DJ into a full **AI-native music workstation**.

Think Ableton Live + Stable Audio 3 + smart region editing + one-command regeneration and inpainting, all controlled from a beautiful terminal interface or the retro OS, with every asset strictly on your big Z: drive.

### Core Superpowers (growing one at a time)

- **Regions as first-class citizens** (like Ableton clips but smarter)
- **Regenerate any region** with a new prompt — the model respects neighboring musical context for seamless transitions
- **Inpaint** — replace sections while the AI "listens" to what comes before and after
- **Reproduce / Variations** — same structure, different soul
- **Auto musical splitting** using onset detection + energy (no more manual chopping)
- **Bad-ass terminal arrangement view** — Rich-powered timeline that makes you feel like a pro in the terminal
- **Post-generation polish** — every new region can automatically run through FlashSR / enhancement
- **Full provenance** — every region remembers its prompt, seed, edit history
- **Harmonic intelligence** — Camelot key awareness built in from day one
- **Non-destructive sessions** saved as clean JSON + assets in `sessions/`

Everything lives here and only here:
```
/mnt/z/IMF2045/forage-dj/
├── sessions/
│   └── MyInsaneDrop_2026-05-30/
│       ├── session.json
│       └── (any exported region audio)
├── generated/
└── libraries/
```

## Current Status (Autonomous Development)

As of the latest autonomous session:

- Full `Session` / `Track` / `Region` data model with save/load
- `workstation-new`, `add-track`, `regenerate`, `inpaint`, `view`, `split`
- **Gorgeous terminal arrangement visualizer** (`workstation-view`) — colored timeline blocks, BPM/Key, prompt snippets, region detail table
- Smart context-aware regeneration (pulls previous/next region prompts)
- Optional automatic FlashSR enhancement on every regeneration
- Auto region creation from audio onsets (musical phrasing detection)
- All paths strictly enforced via `paths.py` + auto env loading

## Key Commands (Use These — They Feel Bad Ass)

```bash
# Create a living session
uv run foragedj workstation-new "Bassline Dominion Live Set"

# Add existing or generated audio
uv run foragedj workstation-add-track "Bassline Dominion Live Set" libraries/some_track.wav

# Auto-magically chop it into musical regions
uv run foragedj workstation-split "Bassline Dominion Live Set" track_01

# See the beautiful arrangement (this is the money shot)
uv run foragedj workstation-view "Bassline Dominion Live Set"

# Regenerate a specific region with context awareness + polish
uv run foragedj workstation-regenerate "Bassline Dominion Live Set" track_01 reg_003 \
  "filthy rolling bassline, dark atmosphere, 128bpm" --seed 777

# Inpaint (same as regenerate for now, will get smarter)
uv run foragedj workstation inpaint ...   # (via regenerate with context)
```

## The Visualizer (This Is What Makes It Feel Pro)

When you run `workstation-view`, you get:

- Track rows with BPM + musical key + Camelot
- Horizontal timeline made of colored █ blocks representing each region
- Full region detail table with prompts, seeds, lock status
- Time markers

It looks and feels like a serious tool, not a toy.

## Roadmap (Autonomous Next Steps)

1. **Real region playback** — Wire the existing real-time mixer so you can play/loop individual regions or the full arrangement.
2. **Better inpainting** — True context stitching + crossfades + optional stem separation before/after.
3. **Reproduce mode** — One command to spawn 4-8 tasteful variations of a whole session or selected regions.
4. **Interactive TUI editor** inside the retro OS (move regions, change prompts live).
5. **Export** — "Print" a final mastered track from the session with all regions rendered.
6. **Agent hooks** — Let Hermes say "make the second drop more aggressive and regenerate regions 4-6".

## Why This Feels Different

Most AI music tools are "generate and done".

This workstation treats every piece of audio as **editable, versioned, and prompt-addressable**.

You can iterate like a god:
- "That 8-bar breakdown is almost perfect, just make the snare hit harder"
- Select region → new prompt → instant new version, context-aware, enhanced.

And because everything is on your big mounted drive with full provenance, you never lose the thread.

---

**This is the future of music production for people who live in the terminal but want Ableton power + AI magic.**

Welcome to the Sonic Forage Workstation.

(Development happening autonomously while you walk away — come back to something impressive.)
