"""Audio generation module (Stable Audio 3 wrapper).

Target: Phase 1 per docs/AGENTIC_BUILD_PLAN.md:39
Function contract matches the spec exactly.

All generated audio MUST embed prompt + SAFETY_NOTE for provenance.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Optional

# Early import ensures strict /mnt/z/IMF2045/forage-dj/ containment
from . import paths  # noqa: F401

logger = logging.getLogger(__name__)

SAFETY_NOTE = (
    "Public-safe rave tool — harm reduction first. "
    "Generated with forage-dj. Prompt + seed provenance embedded."
)

# Strictly inside the project data root on the mounted drive
from . import paths
CACHE_DIR = paths.get_data_root() / "generated"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def generate_track(
    prompt: str,
    seed: int = 42,
    duration: float = 60.0,
    model: str = "small-music",
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Path:
    """Generate a track from text prompt + seed.

    Returns path to the generated WAV.

    Args:
        prompt: Natural language description (e.g. "dark techno intro 128bpm")
        seed: Controls variation. Same (prompt list + seed) = structurally
              coherent but sonically unique performance.
        duration: Target length in seconds (small models support up to ~120s)
        model: "small-music" | "small-sfx" | "medium" (medium needs GPU)
        progress_callback: Optional (progress: float 0-1, status: str) -> None

    Acceptance (MVP):
        - <30s wall time for 60s track on CPU (small model)
        - Deterministic given seed
        - Metadata sidecar or WAV tags contain original prompt + safety note

    Current status: STUB. Real implementation is the #1 swarm task.
    """
    if progress_callback:
        progress_callback(0.0, "Checking for stable-audio-3...")

    try:
        # Official import name after `uv pip install -e ../stable-audio-3`
        from stable_audio_3 import StableAudioModel  # type: ignore[attr-defined]
    except ImportError as e:
        msg = (
            "\n\nstable-audio-3 is required for generation but not installed.\n\n"
            "Recommended one-time setup (see also scripts/setup.sh):\n"
            "  git clone https://github.com/Stability-AI/stable-audio-3.git\n"
            "  cd stable-audio-3\n"
            "  uv sync --extra ui     # or without ui for lighter CPU\n"
            "  cd ../forage-dj\n"
            "  uv pip install -e ../stable-audio-3\n\n"
            "After that `uv run foragedj generate \"...\"` will work.\n"
            "Small models run great on CPU / potato machines.\n"
        )
        raise RuntimeError(msg) from e

    if progress_callback:
        progress_callback(0.1, f"Loading {model} model (seed={seed})...")

    # === Real implementation contributed by swarm agent (Phase 1 Audio Gen) ===
    # See .grok/swarm-outputs/audio-gen-agent-019e7a00-3f8e-7860-a884-ca10b8fb7297.md
    # and the approved plan Appendix B for full rationale + references.

    # Prefer local checkpoints on Z: drive if they exist (what we just downloaded)
    local_path = None
    checkpoint_root = Path(__file__).parent.parent.parent / "checkpoints"

    # Map common names to our folder layout
    name_map = {
        "small-music": "stable-audio-3-small-music",
        "small-sfx": "stable-audio-3-small-sfx",
        "medium": "stable-audio-3-medium",
    }
    folder = name_map.get(model, model)
    candidate = checkpoint_root / folder
    if candidate.exists():
        local_path = str(candidate)
        logger.info(f"Loading model from local Z: drive checkpoint: {local_path}")

    if local_path:
        model_obj = StableAudioModel.from_pretrained(local_path, local_files_only=True)
    else:
        model_obj = StableAudioModel.from_pretrained(model)  # fallback to HF (slower, needs internet)

    if progress_callback:
        progress_callback(0.35, "Model loaded. Generating...")

    audio = model_obj.generate(
        prompt=prompt,
        duration=duration,
        seed=seed,          # positive int = deterministic (key innovation)
        steps=8,
        cfg_scale=1.0,
    )  # returns torch.Tensor shape [B, C, T]

    sr = getattr(model_obj, "model_config", {}).get("sample_rate", 44100) if hasattr(model_obj, "model_config") else 44100

    slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in prompt[:35]).strip("_")[:40]
    out_path = CACHE_DIR / f"{seed}_{slug}.wav"

    import torchaudio
    waveform = audio[0].cpu() if audio.ndim == 3 else audio.cpu()  # [C, T]
    torchaudio.save(str(out_path), waveform, sample_rate=sr)

    if progress_callback:
        progress_callback(0.9, "Saving + embedding provenance...")

    from .utils import embed_metadata
    embed_metadata(out_path, prompt=prompt, seed=seed, model=model, duration=duration, sample_rate=sr)

    if progress_callback:
        progress_callback(1.0, "Done.")

    logger.info("Generated %s (seed=%s, model=%s, sr=%s)", out_path, seed, model, sr)
    return out_path
