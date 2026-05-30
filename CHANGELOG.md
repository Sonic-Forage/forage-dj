# Sonic Forage Changelog

All development happens autonomously inside `/mnt/z/IMF2045/forage-dj/`.

## [Unreleased] — Summer 2026 Launch Push

### Major Additions
- **Full PR/Launch/Streaming Swarm** launched (`skills/pr-launch-and-streaming/`)
- **Live Streaming Guide** + `stream-prep` command (OBS, Twitch/Kick, chat interaction)
- **Workstation v1** — Regions, smart context-aware regeneration + auto-enhance, auto-split, Rich terminal arrangement visualizer
- **Integrations folder** created:
  - Kick Dev API + chat/power chat
  - Twitch EventSub + chat
  - Avaturn reactive avatars (music-reactive characters that listen + bob)
  - MIDI auto-discovery + realtime adaptive mapping
- **Guided CLI first-boot experience** with clear modes (Autonomous DJ, Workstation, Streamer, Collective, Custom)
- **Containment enforcement** — everything forced to live only on the mounted Z: drive

### New Vision Documents
- `docs/ROADMAP.md` — Full tour, gig finding, 12-hour donut raves, harm reduction, multi-performer events, monetization, Avaturn, royalties/collective, festival deals
- `docs/LAUNCH_AND_STREAMING_STRATEGY.md`
- `docs/LIVE_STREAMING_GUIDE.md`
- `docs/WORKSTATION.md`

### Technical Improvements
- Soundfile moved to core deps for reliable audio loading (fixed auto-split issues)
- Robust fallback in region auto-splitting
- Strict path handling via `paths.py` + auto env loading

### Goals for This Phase
- Make money fast for GPUs + tour hardware
- Book first autonomous + multi-performer events (including at least one legal 12-hour underground-style set with donuts)
- Get avatars + chat control working for live streams
- Start small NW Oregon artist collabs + venue outreach

