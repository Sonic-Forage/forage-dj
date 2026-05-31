# What Didn't Work (Institutional Memory)

## Stable Audio Python Backend (The Big One)

- The Python stable-audio-3 models (small-music, small-sfx, medium, open) ultimately did not deliver the audio quality we needed for a serious DJ/music tool.
- Even after significant engineering effort (custom loading, device fixes, local T5Gemma handling, etc.), the results were consistently below what the user gets from good ComfyUI workflows.
- This was the main driver for the major pivot in late May 2026.

## Simple Title-Based Injection in ComfyUI

- The original `comfy_client.py` relied on nodes having specific "title" fields (`prompt`, `seed`, `duration`).
- This works for very simple starter workflows but breaks or becomes painful with real production-grade audio workflows (like the user's ACE-Step and Stable Audio 3 Medium blueprints).
- We needed (and are still building) more general parameter injection that can handle complex graphs with internal logic.

## Keeping Everything on One Branch

- Mixing legacy Python Stable Audio work with the new ComfyUI direction created confusion and technical debt.
- The three-branch strategy (`main` / `legacy/stable-audio` / `beta`) was created specifically to solve this.

## Over-Investing in Local-Only Assumptions

- Early work assumed the ComfyUI server would always be the user's local Windows machine.
- We under-invested in making remote servers (RunPod, Vast, etc.) first-class citizens early enough.

## Trying to Make the Python Backend "Good Enough"

- We spent a lot of time hardening the Python path instead of accepting earlier that ComfyUI was the superior quality route for this project.

---

**Lesson**: When quality is the blocker, be willing to make a hard architectural pivot and preserve history on a branch rather than dragging suboptimal code forward.
