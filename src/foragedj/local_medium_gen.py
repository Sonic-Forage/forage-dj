"""Track 2: Clean Minimal Local Medium Loader for SA3 "medium" checkpoint.

This is the start of the high-ROI clean path that bypasses the fragile
T5GemmaConditioner + MultiConditioner + custom modeling + flash-attn
registration entirely.

GOAL (per AGENTIC_GENERATION_RELIABILITY_PLAN.md):
- Load *only* the DiT (diffusion transformer) + pretransform (autoencoder)
  weights from the user's 9+ GB local Z: checkpoint
  (checkpoints/stable-audio-3-medium/model.safetensors + model_config.json).
- Replace the entire conditioner system with a simple, reliable,
  always-CUDA (or device) text encoder:
    * Preferred: a standard, small, local CLIP text encoder (e.g. openai/clip-vit-base-patch32)
      or sentence-transformers all-MiniLM / paraphrase models (easy, no custom classes).
    * Or a plain local T5 (t5-base or t5-small) via transformers, no Gemma.
- Keep the exact same high-quality medium DiT for generation quality.
- Expose a drop-in compatible `generate_track_local_medium(prompt, seed, duration, ...)`
  or `generate_track(..., model="medium-local")` so CLI / setlist / workstation
  can use it seamlessly.
- Result: reliable local generation from the sacred medium checkpoint
  without ever touching the T5Gemma / SA3 factory conditioner code.

WHY THIS IS NEEDED:
The current monkey-patch in audio_gen.py (LocalT5GemmaConditioner) successfully
loads but still fights internal device/dtype expectations inside
to_cond_embed / sample_flow_pingpong / DiT cross-attn. The patch is a
valiant but high-maintenance workaround.

This file provides the *clean* alternative.

STATUS (this session):
- File skeleton + this plan comment created.
- No implementation yet (next agent or continuation).
- Suggested first steps for implementer:
  1. Study stable_audio_3/loading_utils.py : create_diffusion_cond_from_config
     and how the raw model (pretransform + model) is built from config.
  2. Load the state_dict selectively (filter keys for pretransform.* and model.* / dit.* )
     using load_file + copy_state_dict or manual.
  3. Build a minimal conditioner: just text -> embeddings via a *standard*
     transformers AutoModel + projection if needed. Hardcode to CUDA.
  4. Wire a tiny diffusion sampling loop (or reuse pieces from stable_audio_3.inference
     if they don't pull in the full MultiConditioner).
  5. Test against the known-good previous medium WAV (seed 424242).
  6. Expose via audio_gen.py : if model == "medium-local": delegate to here.
  7. Update CLI choices, health, download (already has the checkpoint), docs.

This is the path that will let users keep using their expensive medium
checkpoint reliably once the open path proves the stack.

See also:
- docs/AGENTIC_GENERATION_RELIABILITY_PLAN.md (Track 2)
- src/foragedj/audio_gen.py (the two fixes + new open path for reference)
- /mnt/z/IMF2045/stable-audio-3/stable_audio_3/ (the lib sources)

Do not remove this file. It is the designated landing zone for the clean loader.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Optional

from . import paths

logger = logging.getLogger(__name__)

# TODO (Track 2 implementer): import the minimal pieces
# from stable_audio_3.loading_utils import load_file, copy_state_dict
# from stable_audio_3.models.pretransforms import ...
# etc. Only what is needed for DiT + AE, no conditioners.


def generate_track_local_medium(
    prompt: str,
    seed: int = 424242,
    duration: float = 60.0,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    # ... other args to match generate_track contract
) -> Path:
    """Stub for the clean local medium path.

    When implemented, this will:
    - Respect require_local=True for the Z: medium checkpoint.
    - Use a simple conditioner (no T5Gemma, no monkey patch).
    - Return WAV with embedded metadata exactly like the main path.

    Until implemented, raises NotImplementedError with pointer to the plan.
    """
    checkpoint_dir = paths.get_checkpoints_dir() / "stable-audio-3-medium"
    if not (checkpoint_dir / "model.safetensors").exists():
        raise FileNotFoundError(
            f"Local medium checkpoint not found at {checkpoint_dir}. "
            "This is required for Track 2."
        )

    if progress_callback:
        progress_callback(0.0, "Track 2 clean medium loader: not yet implemented (see file header)")

    raise NotImplementedError(
        "Track 2 clean minimal loader for medium checkpoint is only scaffolded.\n"
        "See the module docstring in src/foragedj/local_medium_gen.py for the full plan + next steps.\n"
        "Current workaround: use --model open (new default) or --model small-* .\n"
        "Or continue hardening the monkey-patch in audio_gen.py (Track 1)."
    )


# TODO (future):
# - Add a _load_dit_and_pretransform_only(...) helper.
# - Add SimpleTextConditioner or use off-the-shelf embedder.
# - Wire device/dtype hardening from day 1 (the lesson from the patch).
# - Make generate_track() in audio_gen.py dispatch to this for model in ("medium-local", "medium-clean").
# - Add to CLI choices.
# - Health check + validation path.
#
# This file + the plan comment ensure the knowledge and the designated place
# survive agent handoffs.
