---
name: swarm-distribution
description: Autonomous Swarm Distribution App for Sonic Forage. Creates, organizes, analyzes, compiles, and distributes generative music libraries/playlists. Supports seed bombing (autonomous release of generative seeds back into the world) and basic collective royalty tracking.
allowed-tools: ReadFile, WriteFile, Bash(python:*), Bash(uv:*)
compatibility: Linux (primary), cross-platform via uv
metadata:
  author: Sonic-Forage Collective
  version: "0.1.0"
  project: https://github.com/Sonic-Forage/forage-dj
license: MIT
---

# Swarm Distribution App

**Mission**: Autonomously turn generative output (from the workstation, setlists, live sessions) into organized, analyzed, compiled, and distributable packages — then "pump it out" via APIs or self-distribution, while doing seed bombing to spread the culture.

## What the Swarm Can Do (Autonomously)

1. **Create** — Pull from workstation sessions, generate-setlist output, or live recordings.
2. **Organize** — Group by energy, key (Camelot), BPM, vibe, event, etc.
3. **Analyze** — Deep analysis (existing analysis.py + enhancements): energy arcs, harmonic compatibility, danceability estimates, emotional tone from prompts.
4. **Compile** — Build final libraries with:
   - Proper DJ-app metadata (via tag-library)
   - Rich library.json + playlist.txt + transition suggestions
   - Cover art ideas (text prompts for generators)
5. **Distribute** (API stubs + self-hosted):
   - Export ready-to-upload packages for Bandcamp, SoundCloud, self-site, IPFS/Arweave.
   - Basic API hooks (stubs for now — real keys needed per user).
6. **Seed Bomb** — Autonomously release "seeds" (prompt packs, setlist manifests, training configs, generated tracks under permissive licenses) back into the public domain / creative commons to spread the generative mycelium.
7. **Royalties / Collective** — Track usage of shared tracks across sessions. Simple ledger for when people "buy" or use collective music.

## The "People Buying It" Problem + Solution

True full autonomous commercial distribution to Spotify/Apple etc. is hard because:
- Most distributors (DistroKid, CD Baby, TuneCore, Amuse) require human review/approval for new artists.
- Royalties setup needs bank/PayPal + tax info.
- Content policy checks.

**Our autonomous path**:
- **Volume + Quality** via the swarm (pump out analyzed, tagged, ready packages constantly).
- **Seed Bombing** as the viral/gift layer: Release high-quality generative seeds publicly. People discover, use, remix, and some convert to supporters/buyers.
- **Direct + Event Sales**: Sell at gigs, workshops, festivals, via own site + the event/tour system.
- **Collective Model**: Artists contribute tracks → when used in other people's sets or distributed, small royalty share flows back (tracked in session metadata).

The swarm keeps the pipeline running 24/7 so there's always fresh, high-quality material ready.

## How to Run the Swarm

```bash
# Full autonomous pipeline on a session or library
uv run python scripts/swarm_distributor.py --input sessions/MyRaveSession --mode full --seed-bomb --distribute

# Just seed bomb some prompts/setlists
uv run python scripts/swarm_distributor.py --input setlists/ --mode seed-bomb
```

See `scripts/swarm_distributor.py` for current capabilities and TODOs.

## API / Service Ideas for True Autonomy

Current stubs target:
- Self-hosted (own site + IPFS/Arweave for seed bombing — fully autonomous)
- Bandcamp (limited API, good for direct fan support)
- SoundCloud (API exists)
- Future: Look into Amuse, Ditto, or custom distributor APIs if they allow more automation.

For royalties: Start simple with a local ledger + manual payout, or explore blockchain/collective tools later.

## Integration Points

- Uses existing `workstation.py`, `setlist.py`, `analysis.py`, `utils.py` (tag-library)
- Feeds the Event/Tour system (generate material for gigs)
- Works with the PR/Launch/Streaming swarm (content for streams + promotion)
- Can run on tour hardware or a dedicated "distribution rig"

## Seed Bombing Philosophy

"Release seeds back into the world."

Generate:
- Prompt packs
- Locked-seed manifests
- Example libraries
- (Eventually) fine-tuned LoRAs or model configs

Release them publicly (GitHub, IPFS, own site, torrents, USBs at events) under Creative Commons or similar.

People take the seeds, grow their own forests of music, and the culture spreads. Some will come back as supporters, collaborators, or buyers.

This is how we do harm reduction at scale and keep the underground mycelium growing.

## Next Steps for the Swarm

- Real API integrations (start with Bandcamp + IPFS)
- Automated cover art generation prompts
- Better royalty ledger + "collective" sharing in sessions
- Scheduled/cron mode for "keep pumping it out"
- Connection to live events (auto-prepare packages from a gig recording)

This is the engine for turning the workstation into a real distribution + cultural force.

Run it. Pump it out. Seed bomb. Build the collective.
