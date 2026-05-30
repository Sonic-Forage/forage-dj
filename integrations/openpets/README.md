# OpenPets Integration for Sonic Forage

**Repo**: https://github.com/alvinunreal/openpets

## What is OpenPets?

OpenPets is a delightful desktop companion app that puts a cute pixel-art pet on your screen. The pet can:
- Idle and react with animations
- Show speech bubbles
- Be controlled by AI agents via MCP (Model Context Protocol)
- Run as a standalone fun desktop buddy or deeply integrated with coding/AI tools

It supports custom "pet packs" so you can make your own characters.

## Vision for Sonic Forage: Mini DJ Companions

We want to turn OpenPets into **living desktop DJ mascots** that hang out with you while you use the workstation.

Imagine:
- A tiny **Neon** pet chilling in the corner of your screen while you edit regions in the workstation.
- You click the pet → it pops up a little chat panel.
- You talk to it (using Grok TTS voice) and say "make this drop darker" or "evaluate this region".
- The pet reacts, suggests prompts, helps generate, or even triggers `regenerate_region` / `swarm-distribute`.
- During a live set or autonomous Docker session, the pet bobs to the music (we can feed it playback data) and gives hype or chill reactions.
- For streams/events: the pet becomes part of the visual identity (projected, in OBS, etc.).

This combines beautifully with:
- Our **AI DJ Personalities** system (the pet *is* one of the single-name DJs like Neon, Flux, Bloom, etc.)
- **Avaturn** (the 3D reactive version for bigger screens)
- **HeyGen HyperFrames + Rex** (the talking video version for promotion)
- The **media player** and **retro OS**

## Quick Start (Desktop Pet + Forage-dj)

1. Download and install OpenPets from their releases.
2. Launch it — you get a default cute pet.
3. (Advanced) Connect it via MCP so our tools can control it.

## Making Your Own Mini DJ Pets (The Fun Part)

Using our `data/ai_dj_personalities/personalities.json`:

Each personality (Neon, Vapor, Pulse, Echo, Flux, etc.) can have its own custom pet pack with:
- Idle "chilling" animation (head bobbing, subtle movement)
- Reactions to generation events (thinking face when regenerating a region, hype dance on successful seed bomb)
- Different color palettes matching the music style vibe
- Speech bubble style that matches their catchphrases

### Suggested Mini DJ Pet Concepts

- **Neon** → Cyberpunk pixel pet with glowing edges, subtle matrix rain in background when thinking.
- **Vapor** → Vaporwave aesthetic pet (palm tree, grid floor, slowed animations).
- **Pulse** → High-energy bouncy pet that literally pulses with the BPM we feed it.
- **Bloom** → Soft plant/animal hybrid pet that "grows" flowers when good music plays, gives water reminders.
- **Flux** → Glitchy, shifting pet that occasionally "breaks" and reforms.

We can create these as custom pet packs (OpenPets supports loading animated pixel art packs).

## Interactive Side Panel / Click-to-Talk

The user wants: "a panel pops up on side of screen chilling click to talk help make track evaluate"

OpenPets pets already live on the desktop. We can enhance the experience with:

- Click the pet → opens a small always-on-top chat window (we can build a tiny Electron/Tauri sidecar or use the pet's existing speech system + Grok backend).
- The pet uses the current **AI DJ Personality** (or lets you switch).
- Chat with it using Grok TTS voice output.
- Commands it understands:
  - "Evaluate this region" → calls our analysis + gives feedback in character voice.
  - "Make the bass darker" → generates a new prompt and triggers `regenerate_region`.
  - "Help me with the next drop" → suggests from the personality's favorite styles.
  - "Seed bomb this" → triggers swarm distribution.

This turns the pet into a real creative collaborator that lives on your desktop while you work.

## Integration Points with Existing Sonic Forage Systems

- **Personalities system** (`src/foragedj/personalities.py`): The pet *embodies* one of our DJs. Switching personalities changes the pet's look + voice + behavior.
- **Media Player / Workstation**: Feed real-time playback data (current BPM, energy, region prompt) so the pet reacts live (bobs harder on high energy, looks thoughtful during breakdown).
- **Swarm Distribution + Seed Bombing**: Pet gets excited and does a little celebration animation when a new seed is released.
- **Docker Autonomous Sessions**: Even in headless/scheduled mode, we can still drive a pet on a secondary monitor for visual flair during events.
- **Retro OS**: Add a "Summon Pet" button in the OS that launches the matching OpenPets character for the current session's personality.
- **Rave Prep / Harm Reduction**: The pet can occasionally drop PLUR reminders or "hydrate" messages.

## Setup for "Rex" Style Promotion (with Grok TTS + HeyGen)

See also `integrations/hyperframes/`.

We can create a talking video version of the same personalities using HeyGen + Grok TTS as "Rex the Official Sonic Forage Guide". The desktop pet is the always-present chill version; the video version is for marketing and onboarding.

## Next Autonomous Steps

1. Create sample pixel art descriptions / animation specs for 3-4 starter mini DJ pets (Neon, Bloom, Flux, Pulse).
2. Build a small bridge script that lets our CLI/tools send reactions/speech to a running OpenPets instance via its MCP server.
3. Add a "Pet Companion" toggle in the retro OS and workstation.
4. Generate a few fun demo videos using HyperFrames + the personalities as Rex variants.

This is one of the most charming and "bad ass" ways to make the tool feel alive and approachable — especially for events, streams, and workshops where having a cute little DJ buddy on screen makes everything more fun and memorable.

OpenPets gives us the desktop presence layer. Our personalities + workstation give it soul and actual creative power.

Let's make some mini DJs. 🐾🎛️
