# 🍓 Sonic Forage — Mission Guide & Interactive Walkthrough

**"The bass is strong with this one"**

Welcome to the world's first (mostly) autonomous open-source AI DJ operating system.

This document is your friendly, slightly unhinged guide to the whole mycelium.

---

## The Big Idea (PLUR + AI)

We are not here to replace DJs.

We are here to give every human (and future AI agent) the power to:

- Write a **setlist as a prompt score**
- Lock a **seed** for infinite unique performances of the *same* structure
- Walk away while the machine generates a full harmonically-mixed library
- Come back to something ready to drop in a real set or festival

All while staying true to **Peace, Love, Unity, Respect** and real harm reduction.

---

## Core Workflow (Super Easy Mode)

1. **One-time setup**
   ```bash
   ./scripts/setup.sh
   uv run foragedj doctor
   ```

2. **Download the good stuff** (models + LoRAs)
   ```bash
   export HF_TOKEN=hf_your_token
   uv run foragedj download-models
   ```

3. **Create or use a locked setlist manifest** (see `setlists/`)

4. **Generate & walk away**
   ```bash
   uv run foragedj generate-setlist --manifest setlists/bassline_dominion_seed424242.yaml
   ```

5. **Come back** to `libraries/Your_Set_SeedXXXX/` containing:
   - All WAVs
   - `library.json` (BPM, key, Camelot, energy, recommended transitions)
   - `playlist.txt` (old-school Winamp vibes for your DJ software)

6. **Play / Mix**
   - Use the real-time mixer (`foragedj mix` or GUI)
   - Or the upcoming Unicode CDJ / Winamp-style library player

---

## The Magic: Setlist as Score + Seed Variation

One manifest + one seed = one unique performance.

Change only the seed → completely different realization while keeping the energy arc, BPM relationships, and harmonic journey.

This is the core innovation. Share the manifest. Everyone gets their own version.

---

## LoRAs & Style Transfer (Easy Access)

All Sonic-Forage SA3-compatible LoRAs live in `checkpoints/loras/`.

Use them via the standard `stable-audio-3` library (LoRA training/inference docs in the upstream repo).

Examples already wired into the downloader:
- NPS Liminal Soundscapes
- Loopwyrm Smoke
- Didgeridoo Earth Drone
- Drama Box NASA Radio
- LTX23 SFX Drops
- ...and whatever else appears in the Sonic-Forage HF org

---

## Future Autonomous Agent Integration

This whole system is designed to be *agent-usable*.

See `docs/HERMES_INTEGRATION.md` for how forage-dj can become a set of tools/skills for systems like Hermes Agent (Nous Research).

Imagine an agent that:
- Curates a setlist based on festival data + weather + crowd sentiment
- Generates the library overnight
- Exports it as a fresh training dataset
- Books the gig (with human approval gate, of course)

---

## How to Contribute / Play

- Fork the manifests
- Train your own LoRAs on your sound
- Export your libraries as public datasets
- Build new players (Winamp skins welcome)
- Add more autonomous agent skills

Everything is given away because **starting a movement > getting paid**.

---

**PLUR forever. Fork it. Build it. Play it.**

*This guide is intentionally a bit unhinged. That is on purpose.*
