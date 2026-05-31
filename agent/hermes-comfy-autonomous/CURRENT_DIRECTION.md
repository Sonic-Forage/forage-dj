# Current Direction (as of late May 2026)

## The Big Decision

We are moving **all-in** on ComfyUI for music generation in ForageDJ.

**Primary engine**: ComfyUI running ACE-Step 1.5 XL Turbo (and other high-quality audio workflows the user brings).

**Why**:
- Significantly better audio quality than the Python Stable Audio 3 models.
- Extremely flexible — the user can bring almost any workflow.
- Works great with remote GPU servers (RunPod, Vast.ai, etc.).
- Supports complex internal logic (prompt engineering, lyrics handling, etc.) inside the workflow itself.

## What Changed

- The old Python Stable Audio backend (small/medium models, the whole `stable-audio-3` integration) has been deprioritized.
- All that code and related work lives on the `legacy/stable-audio` branch.
- `main` is now ComfyUI-first.
- We are building toward the user being able to run ForageDJ + ComfyUI (local or remote) and have music generate autonomously in the background while they code or live their life.

## Core Experience We're Aiming For

1. User points ForageDJ at a ComfyUI server (could be their Windows box via Tailscale or a remote pod).
2. User can trigger generation easily, or set up autonomous/background generation.
3. Newly generated tracks flow into a "radio" experience the user can listen to while working.
4. The system feels like a creative collaborator that keeps making music for you.

## What "Good" Looks Like Right Now

- Easy, reliable way to generate with the user's ACE-Step 1.5 XL Turbo workflow (and future workflows).
- Clean support for remote ComfyUI servers.
- The terminal radio (PowerShell version + future improvements) actually feels like a live station.
- A remote Hermes agent can pick up this `agent/hermes-comfy-autonomous/` folder and meaningfully advance the work.

## What We're Not Doing (for now)

- Heavy investment in the old Python Stable Audio models on `main`.
- Trying to make the Python backend compete on quality with ComfyUI.

This direction is simpler and higher leverage: leverage the best tool for the job (ComfyUI) and build the autonomous DJ experience on top of it.
