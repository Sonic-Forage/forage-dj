#!/usr/bin/env python3
"""
forage-dj Model Checkpoint Downloader

Downloads the required Stable Audio 3 models + autoencoders + NEW:
  - Audio enhancement / super-resolution (AudioSR + FlashSR variants)
  - Voice quality tools (LocalVQE for real-time AEC/denoise/dereverb)
  - TTS / vocal synthesis (Kokoro-82M lightweight high-quality)

Everything lands under `checkpoints/` (and HF cache pinned to Z:).

Usage:
    source .grok/hf-cache.env
    export HF_TOKEN=hf_your_token   # only needed for gated SA3
    uv run python scripts/download_checkpoints.py [--group core|enhancers|voice|all]

Groups:
  core       = Stable Audio 3 + SAME + Sonic-Forage LoRAs (default if no flag)
  enhancers  = FlashSR (tiny fast + laion one-step) + AudioSR (high quality diffusion)
  voice      = LocalVQE GGUF (CPU real-time voice cleaner) + notes for Kokoro TTS
  all        = everything above

See docs/MODEL_ACCESS.md + docs/ENHANCEMENT_TOOLS.md for details + licenses.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

from huggingface_hub import snapshot_download, hf_hub_download
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"

# Core Stable Audio 3 models + autoencoders (user requested)
CORE_MODELS: List[Tuple[str, str]] = [
    ("stabilityai/stable-audio-3-small-music", "stable-audio-3-small-music"),
    ("stabilityai/stable-audio-3-small-sfx",   "stable-audio-3-small-sfx"),
    ("stabilityai/stable-audio-3-medium",      "stable-audio-3-medium"),
    ("stabilityai/stable-audio-3-optimized",   "stable-audio-3-optimized"),
    ("stabilityai/SAME-S",                     "SAME-S"),
    ("stabilityai/SAME-L",                     "SAME-L"),
]

# Sonic-Forage community LoRAs & compatible checkpoints (from https://huggingface.co/Sonic-Forage)
# These are SA3-compatible LoRAs / adapters for fine-tuning / style.
SONIC_FORAGE_LORAS: List[Tuple[str, str]] = [
    ("Sonic-Forage/nps-liminal-soundscapes-lora-v0-1", "loras/nps-liminal-soundscapes-lora-v0-1"),
    ("Sonic-Forage/loopwyrm-sa3-lora-smoke-v0-1", "loras/loopwyrm-sa3-lora-smoke-v0-1"),
    ("Sonic-Forage/didgeridoo-earth-drone-medium-v1-merged-comfy-checkpoint", "checkpoints/didgeridoo-earth-drone-medium-v1-merged"),
    ("Sonic-Forage/didgeridoo-earth-drone-medium-v1-standard-comfy-lora", "loras/didgeridoo-earth-drone-medium-v1-standard"),
    ("Sonic-Forage/dramabox-nasa-radio-talk-lora", "loras/dramabox-nasa-radio-talk-lora"),
    ("Sonic-Forage/ltx23-sonic-forage-sfx-drops-lora-v1", "loras/ltx23-sonic-forage-sfx-drops-lora-v1"),
]

ALL_MODELS = CORE_MODELS + SONIC_FORAGE_LORAS

# === NEW: Audio Enhancement / Super-Resolution models (2025 stack) ===
# FlashSR (YatharthS tiny version): 2MB/500KB, 200-400x realtime 16kHz->48kHz. Speed king.
# laion FlashSR one-step (2025 distilled): ~3GB total, much better quality, still fast single-pass.
# AudioSR (drbaph port): ~6GB each, highest quality latent diffusion (slow, 50-100 steps). Two variants.
ENHANCERS: List[Tuple[str, str]] = [
    ("YatharthS/FlashSR", "enhancers/flashsr-tiny"),
    ("laion/FlashSR_One-step_Versatile_Audio_Super-resolution", "enhancers/flashsr-onestep"),
    ("drbaph/AudioSR", "enhancers/audiosr"),
]

# === NEW: Voice tools ===
# LocalVQE (LocalAI-io): Tiny real-time CPU model for joint AEC + noise suppression + dereverberation.
# GGUF files are tiny (5-19 MB). Best inference via their C++/GGML build (see GitHub).
# Kokoro-82M TTS is loaded on-demand by the `kokoro` package (Apache, 82M params, excellent quality,
# many voices, streams fast). It auto-caches into your HF_HOME (Z: pinned). No manual snapshot needed.
VOICE_TOOLS: List[Tuple[str, str]] = [
    # We download only the key GGUF files (targeted) instead of full repo for speed
    # The repo also hosts .pt PyTorch versions if you prefer research use.
]

# Kokoro note: run `uv run foragedj speak "hello world"` after `pip install kokoro soundfile`
# (plus system espeak-ng for G2P). It will pull weights automatically to the pinned HF cache.

def download_model(repo_id: str, local_name: str, token: str | None = None) -> Path:
    target_dir = CHECKPOINTS_DIR / local_name
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Downloading {repo_id} → {local_name} ===")
    print(f"Target: {target_dir}")

    # Modern snapshot_download call (deprecated resume/symlink args removed).
    # When local_dir is provided, files land directly (no symlinks to cache).
    # HF cache (HF_HOME etc.) still used for efficiency; token enables gated access + higher rate limits.
    ignore = ["*.git*", "*.md", "onnx/*"] if "optimized" not in local_name else None
    local_path = snapshot_download(
        repo_id=repo_id,
        local_dir=str(target_dir),
        ignore_patterns=ignore,
        token=token,
    )

    print(f"✓ Finished: {local_path}")
    return Path(local_path)


def download_voice_tools(token: str | None = None) -> None:
    """Targeted download of small GGUF files for LocalVQE (real-time voice cleaner)."""
    voice_dir = CHECKPOINTS_DIR / "voice" / "localvqe"
    voice_dir.mkdir(parents=True, exist_ok=True)

    files = [
        ("localvqe-v1.3-4.8M-f32.gguf", "19 MB - wider/better noise handling"),
        ("localvqe-v1.2-1.3M-f32.gguf", "5 MB - fastest CPU option"),
    ]

    print("\n=== Downloading LocalVQE voice enhancement GGUF files ===")
    print("Target:", voice_dir)
    print("These are tiny and run real-time on CPU for AEC + denoise + dereverb.\n")

    for fname, desc in files:
        try:
            print(f"  → {fname} ({desc})")
            path = hf_hub_download(
                repo_id="LocalAI-io/LocalVQE",
                filename=fname,
                local_dir=str(voice_dir),
                token=token,
            )
            print(f"    ✓ {path}")
        except Exception as e:
            print(f"    ⚠️ Could not fetch {fname}: {e}")
            print("       (You can manually download from https://huggingface.co/LocalAI-io/LocalVQE)")

    print("\nLocalVQE ready. For best speed build the C++ GGML engine from:")
    print("  https://github.com/localai-org/LocalVQE  (nix or cmake, very fast on CPU)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="forage-dj checkpoint + enhancement/voice downloader")
    parser.add_argument("--group", choices=["core", "enhancers", "voice", "all"], default="all",
                        help="What to download (default: all for the full Music Diffusion OS experience)")
    args = parser.parse_args()

    print("forage-dj Checkpoint + Enhancement/Voice Downloader")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Checkpoints target: {CHECKPOINTS_DIR}")
    print(f"Group: {args.group}")

    hf_home = os.environ.get("HF_HOME", "NOT SET")
    print(f"HF cache: {hf_home}")
    if "NOT SET" in hf_home:
        print("   ⚠️  Run the installer or: source .grok/hf-cache.env (Linux/mac) or .grok/hf-cache.ps1 (Windows)")

    token = os.environ.get("HF_TOKEN")
    if token:
        print("HF_TOKEN: detected (gated SA3 + faster downloads)")
    else:
        print("HF_TOKEN: not set (fine for most enhancers/voice tools; needed only for Stability)")

    print("\n" + "=" * 64)
    print("⚠️  STABILITY AI MODELS ARE GATED (core group)")
    print("=" * 64)
    print("For core SA3 models you must accept licenses + provide token.")
    print("Enhancers (FlashSR / AudioSR) and Voice tools (LocalVQE) are generally open.")
    print("See docs/MODEL_ACCESS.md for the full list of 'Agree' links.\n")

    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

    results: List[Tuple[str, str, bool, str | None]] = []

    do_core = args.group in ("core", "all")
    do_enh = args.group in ("enhancers", "all")
    do_voice = args.group in ("voice", "all")

    if do_core:
        print("\n>>> Downloading CORE (Stable Audio 3 + LoRAs)")
        for repo_id, local_name in ALL_MODELS:
            try:
                download_model(repo_id, local_name, token=token)
                results.append((repo_id, local_name, True, None))
            except GatedRepoError as e:
                msg = "GATED: Accept license on HF page + valid HF_TOKEN"
                print(f"🔒 {msg} — {repo_id}")
                results.append((repo_id, local_name, False, str(e)[:200]))
            except (HfHubHTTPError, RepositoryNotFoundError) as e:
                err_str = str(e)
                msg = "AUTH/HTTP error" if any(x in err_str.lower() for x in ("401","403","gated","access")) else f"Error: {err_str[:120]}"
                print(f"❌ {msg} — {repo_id}")
                results.append((repo_id, local_name, False, err_str[:200]))
            except Exception as e:
                print(f"❌ ERROR {repo_id}: {e}")
                results.append((repo_id, local_name, False, str(e)[:200]))

    if do_enh:
        print("\n>>> Downloading ENHANCERS (Audio Super-Resolution + Enhancement)")
        print("  • flashsr-tiny     = blazing fast (200-400x RT), tiny files — great default for live")
        print("  • flashsr-onestep  = 2025 distilled one-step (excellent quality/speed balance)")
        print("  • audiosr          = highest quality (diffusion, slow, ~6 GB each variant)\n")
        for repo_id, local_name in ENHANCERS:
            try:
                download_model(repo_id, local_name, token=token)
                results.append((repo_id, local_name, True, None))
            except Exception as e:
                print(f"⚠️  Enhancer {repo_id}: {e} (non-fatal, many are open weights)")
                results.append((repo_id, local_name, False, str(e)[:200]))

    if do_voice:
        download_voice_tools(token=token)
        # Kokoro is auto-pulled by the package on first `speak` use into the Z: HF cache
        print("\n>>> Voice note: Kokoro-82M TTS (best lightweight high-quality open TTS)")
        print("    It will be fetched automatically the first time you run:")
        print("        uv run foragedj speak \"welcome to the sonic forage\"")
        print("    Requires: uv pip install kokoro soundfile  + system package 'espeak-ng'\n")

    # === SUMMARY ===
    print("\n" + "=" * 64)
    print("DOWNLOAD SUMMARY")
    print("=" * 64)
    successes = [r for r in results if r[2]]
    failures = [r for r in results if not r[2]]
    print(f"Processed: {len(results)}  |  Success: {len(successes)}  |  Issues: {len(failures)}")

    if successes:
        print("\nSuccessful:")
        for repo, local, _, _ in successes:
            print(f"  • checkpoints/{local}  ← {repo}")

    if failures:
        print("\nHad issues (often non-fatal for open enhancers/voice):")
        for repo, local, _, err in failures:
            print(f"  • {local} ← {repo}")
            if err:
                print(f"      {err[:140]}")

    print("\nPotato / offline workflow (Linux + Windows):")
    print("  # Linux / mac / WSL")
    print("  source .grok/hf-cache.env && export HF_TOKEN=... && uv run python scripts/download_checkpoints.py --group all")
    print("  # Windows PowerShell")
    print("  . .grok\\hf-cache.ps1 ; $env:HF_TOKEN=... ; uv run python scripts/download_checkpoints.py --group all")
    print("  Large files live under your configured data root (Z:, D:, E:, or project/data/)")
    print("\nNext:")
    print("  • uv run foragedj doctor --heal")
    print("  • uv run foragedj enhance --help     (new audio upscaler tool)")
    print("  • uv run foragedj speak --help       (Kokoro TTS)")
    print("  • uv run foragedj clean-voice --help (LocalVQE)")
    print("=" * 64)
    print("Done. Your Music Diffusion OS just got better ears and a voice. 🎛️🔊")


if __name__ == "__main__":
    main()
