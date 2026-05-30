---
name: forage-dj-pr-launch-streaming
description: Launch swarm for PR, marketing, community, and real-world live streaming strategy for the Sonic Forage Music Diffusion Workstation. Includes Twitch/Kick integration plans, content strategy, onboarding improvements, and "stream-ready" technical features.
allowed-tools: ReadFile, WriteFile, Bash(python:*), Bash(uv:*)
compatibility: All platforms (focus on Linux for dev, Windows for many streamers)
metadata:
  author: Sonic-Forage Collective
  version: "0.1.0"
  project: https://github.com/Sonic-Forage/forage-dj
license: MIT
---

# PR, Launch & Streaming Swarm — Sonic Forage Workstation

**Goal**: Turn this powerful local AI music workstation into something real humans (streamers, live performers, bedroom producers) can actually discover, understand, and use on Twitch, Kick, and IRL.

We have a genuinely unique product:
- Fully local, private, improving over time
- Retro OS + terminal DAW workstation
- Generative + editable + regeneratable regions (the new workstation features)
- Hardware control (MIDI/OSC)
- Self-healing

But right now it's hard for normal people to jump in and go live.

This swarm exists to fix that and build real momentum.

## Swarm Roles (Launch These Agents)

### 1. Marketing & Positioning Lead
- Craft the core narrative: "The first Music Diffusion Operating System — local, editable, streamable"
- Create taglines, one-pagers, tweet threads, YouTube descriptions
- Differentiate vs Udio/Suno (local + editable + workstation, not just generation)

### 2. Streaming & Live Performance Specialist
- Full guide for going live on Twitch/Kick with forage-dj
- Recommended OBS scenes, audio routing, clean terminal visuals
- "Chat-controlled generation" ideas (viewers suggest prompts via commands)
- Low-latency performance tips
- IRL / club performance strategy (RunPod or beefy local rig)

### 3. Onboarding & First-Time Experience Agent
- Improve `scripts/install.py`, `doctor --heal`, and welcome messages
- Create "30 seconds to your first stream" quickstart
- "Stream Ready" mode / preset in the retro OS and CLI
- Beautiful default visuals and themes for OBS capture

### 4. Content & Community Manager
- 30-day launch content calendar (Twitch, TikTok, YouTube Shorts, X)
- Ideas for "building in public" while improving the tool live on stream
- Community Discord/Telegram structure
- Beta tester program for serious streamers and producers

### 5. Technical Streaming Features Agent
- Add `--stream` / stream mode flags
- Clean high-contrast terminal themes for capture
- Easy "export current session for VOD" 
- OBS-friendly visualizer improvements
- Hotkey / MIDI bindings optimized for live performance

### 6. PR & Press Outreach Agent
- Media list (music tech, AI, live performance, electronic music blogs)
- Press kit (screenshots, short demo videos, one-pager)
- Story angles: "Fully local AI DAW", "The Ableton of diffusion", "Private generative music workstation"

## How to Launch This Swarm

1. **Human (you)** reads this skill and the main `docs/WORKSTATION.md` + `docs/INSTALL.md`.

2. Spawn agents by giving them focused sub-prompts based on the roles above. Each agent should:
   - Work only inside `/mnt/z/IMF2045/forage-dj/`
   - Produce concrete artifacts (docs, code changes, scripts, graphics plans)
   - Update `docs/LAUNCH_STATUS.md` with progress

3. Use the existing agent patterns in `agent/` and `.grok/swarm-outputs/`.

## Immediate High-Impact Actions (Do These First)

### A. Make It Actually Usable for Streams (Technical)
- Add a `--stream` mode to the retro OS that:
  - Uses high-contrast retro theme optimized for OBS
  - Shows big, clean BPM/Key + current prompt
  - Has a "Chat Prompts" panel (even if manual for now)
- Improve the visualizer and workstation-view for screen capture (bigger text, less clutter)
- Add one-command "go live prep":
  ```bash
  uv run foragedj stream-prep --obs --twitch
  ```

### B. Documentation That Converts
- World-class `docs/LIVE_STREAMING_GUIDE.md` (Twitch + Kick focused)
- "From zero to first live set in 20 minutes" guide
- Case studies / example streams (even if simulated at first)

### C. Narrative & Positioning
- Finalize the "Music Diffusion OS" + "AI-Native Workstation" positioning
- Create 3 killer demo video scripts (30s hook, 3min deep, 8min full performance)

## Success Metrics (for this swarm)

- First 5 external people successfully run a full stream or live set using the tool
- At least one "building in public" Twitch/Kick series running
- Clear, exciting onboarding that doesn't require reading 10 docs first
- Growing waitlist or Discord of interested streamers/producers

## Notes on Quality & Local-First Reality

Quality is currently "good enough and improving fast" because:
- Everything runs locally on your hardware
- You control the models and can swap in better ones as they appear
- The workstation editing + regeneration loop lets you fix problems in real time

This is actually a **strength** for serious creators who care about ownership and iteration, unlike cloud-only tools.

Lean into the "local, private, improvable, editable" story.

---

**This swarm's job is to turn a powerful but hidden gem into something people are excited to discover, try, and go live with.**

Start by claiming roles above and producing real artifacts inside this repo only.

Let's get this thing in front of real audiences. 🍓📺🎛️
