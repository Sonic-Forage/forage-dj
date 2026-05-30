# Sonic Forage — Full Roadmap & Vision (Summer 2026+ Tour Launch)

**Status**: Launch mode. User needs money fast for GPUs + hardware. Everything strictly in `/mnt/z/IMF2045/forage-dj/`.

## Core Thesis
A fully local, private, editable **Music Diffusion Operating System** that becomes a real-world performance tool, harm-reduction platform, community collective, and revenue engine for live events, festivals, clubs, raves, and workshops.

## Current State (What We Have Right Now — All in Root)
- Full workstation (regions, smart context-aware regenerate + auto-enhance, auto-split, bad-ass Rich timeline visualizer)
- Retro OS TUI desktop
- Real-time mixer + visualizer
- Enhancement stack (FlashSR, AudioSR, LocalVQE, Kokoro)
- PR/Streaming Swarm fully launched (`skills/pr-launch-and-streaming/`)
- Live streaming guides + `stream-prep` command
- Kick + Twitch + Avaturn + MIDI auto-map integration stubs in `integrations/`
- Cross-platform installers
- Strict containment via `paths.py` + auto env loading + `.grok/` helpers

## Phase 1 — Immediate Launch (Next 4-8 Weeks) — "Get Money + GPUs"
**Goal**: Make money fast so we can tour and give the tool away.

### 1.1 Gig & Event Finding System (Autonomous)
- Script/agent that scrapes or suggests venues: underground raves (legal), nightclubs, strip clubs, small festivals, warehouses in PNW.
- CLI command: `foragedj tour-find --region "PNW" --type "12hour-rave"`
- Booking templates, rider (needs GPU rig + good audio + projectors for avatars).

### 1.2 First Signature Event
- **12-hour underground legal rave** (8pm–8am) — "Donut Rave" harm reduction concept.
  - Autonomous DJ sets (forage-dj workstation + live regeneration).
  - Free donuts + water + harm reduction info.
  - Multiple performers: magicians, poi/spin artists, foam/paint people, clowns.
  - Avaturn characters on screens reacting to the music.
  - Pass out flyers with QR to the project (give the software away).

### 1.3 Monetization Paths (Fast Cash)
- Paid private installs/workshops at clubs & events.
- "Collective" model: Artists upload tracks → when used in other people's sets, small royalty share (metadata in session.json).
- Festival deals + big artist collabs (start with small NW Oregon artists).
- Merch + "Donut Rave" ticket model.

### 1.4 Hardware Money Goal
- Target: Enough cash for strong local GPU rig(s) + multiple laptops for tour/events.

## Phase 2 — Tour + Ecosystem (Summer 2026 Onward)
- Multi-city / PNW tour with pop-up autonomous + multi-performer events.
- Workshop series at raves/festivals teaching people to run their own autonomous systems.
- Full Avaturn integration: characters that listen to the music, bob, react, have pop-up encouragement UI. Fine-tune on our generated + performed dataset.
- MIDI auto-map + realtime adaptation (plug controller → system learns best mappings for live performance).
- Chat-controlled autonomous DJ on Twitch + Kick (using the integrations we added).

## Phase 3 — Collective & Distribution
- True community collective: shared music library with royalty tracking when tracks are reused.
- Easy export/distribution to platforms.
- Connections to bigger artists, labels, festival bookers.
- Open source core + paid premium event tools.

### Docker + Scheduled Autonomous Deployment (New)
- Full containerized deployment for dedicated machines or tour rigs.
- Smart entrypoint supports `SHOW_TIME=20:00` + `BOOT_EARLY_MINUTES=45` so the container wakes up with enough time to load huge models and prepare the set.
- Perfect companion to the Swarm Distribution App and Event/Tour system.
- See `docs/DOCKER_DEPLOYMENT.md` and `docker/` folder.

### Swarm Distribution App (New Autonomous Engine)
- Full pipeline: create (from workstation/sessions) → organize → analyze (deep harmonic/energy) → compile (DJ-tagged libraries) → distribute.
- `foragedj swarm-distribute --input ... --mode full --seed-bomb`
- **Seed Bombing**: Autonomously release generative seeds (prompt packs, manifests, tracks under CC) back into the world via IPFS/self-site to spread the culture virally.
- Royalty/collective tracking built into session metadata.
- Keeps "pumping it out" at volume so the only real limit becomes discovery and people buying/supporting (solved via seed bombing + events + direct sales).

This is how we turn one person's creative output into a self-replicating, royalty-generating mycelium.

## Technical Roadmap Priorities (in order)
1. **Containment & Polish** (current) — Everything 100% in root, no leaks.
2. **Tour/Gig Tools** — `tour-find`, event planning scripts, harm reduction presets.
3. **Avaturn + Visuals** — Reactive characters tied to workstation regions + audio features.
4. **AI DJ Personalities + HyperFrames** — 111+ music styles + customizable single-name DJs (Neon, Vapor, etc.) for autonomous sets, chat, and promotional "Rex" interactive videos using Grok TTS + HeyGen.
5. **MIDI Auto-Map** — Full auto discovery + adaptive mapping.
5. **Chat Control** — Real Kick/Twitch listeners feeding prompts/regenerations.
6. **Monetization Layer** — Simple royalty metadata + collective sharing in sessions.
7. **Event Deployment** — One-command "install autonomous system at venue" (with avatars, multi-performer support).
8. **12-Hour Rave MVP** — Full production plan for first legal donut rave.

## Harm Reduction & Culture
- Core value: Give the tool away at events.
- Donuts + water + education at every big set.
- Autonomous systems that can run safely without constant human oversight (with good defaults + monitoring).
- Goal: Make powerful AI music tech accessible and safe in underground + club scenes.

## Success Metrics (Summer 2026)
- At least 1 successful 12-hour legal donut rave with multiple performers + avatars.
- 5+ paid gigs or workshops booked autonomously.
- Enough revenue for multiple GPU rigs + tour computers.
- First small NW Oregon artist collabs.
- Growing list of venues/clubs interested in permanent autonomous installs.
- Active Twitch/Kick streams using the tool with chat interaction.

---

**We are building something that can actually tour, make money, give value away, and spread the tech responsibly.**

This is the truth. Let's launch.
