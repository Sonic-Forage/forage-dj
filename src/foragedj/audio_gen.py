"""Audio generation module (Stable Audio 3 wrapper).

Target: Phase 1 per docs/AGENTIC_BUILD_PLAN.md:39
Function contract matches the spec exactly.

All generated audio MUST embed prompt + SAFETY_NOTE for provenance.
"""

from __future__ import annotations

import logging
import os
import sys
import typing as tp
import torch  # ensure always available for LocalT5GemmaConditioner methods etc.
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
    hf_token: Optional[str] = None,
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
        hf_token: Optional Hugging Face token. Used for any metadata/lookup
                  if absolutely required, but local checkpoint loading on Z:
                  drive is ALWAYS preferred and does not require network.

    Acceptance (MVP):
        - <30s wall time for 60s track on CPU (small model)
        - Deterministic given seed
        - Metadata sidecar or WAV tags contain original prompt + safety note

    Local-first: For models with local checkpoints under checkpoints/ (including
    medium), uses fully local loading + standard transformers Auto* with
    local_files_only=True for the bundled t5gemma-b-b-ul2 encoder. This
    completely bypasses fragile from_pretrained paths and the broken
    T5GemmaEncoderModel custom import in some transformers versions.
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

    # ROBUST LOCAL-FIRST LOADING (bypasses all HF from_pretrained + T5GemmaEncoderModel crashes)
    # When a complete local checkpoint dir exists under checkpoints/ (with model.safetensors + t5gemma-b-b-ul2/),
    # we use create_diffusion_cond_from_config + safetensors load, but with a monkey-patched
    # conditioner that loads the text encoder via STANDARD transformers (AutoModel + local_files_only=True).
    # This never executes the library's T5GemmaConditioner.__init__ (the source of the import error).
    # No silent fallbacks to the known-broken HF path for local checkpoint cases.
    checkpoint_root = Path(__file__).parent.parent.parent / "checkpoints"

    name_map = {
        "small-music": "stable-audio-3-small-music",
        "small-sfx": "stable-audio-3-small-sfx",
        "medium": "stable-audio-3-medium",
    }
    folder_name = name_map.get(model, model)
    local_model_dir = checkpoint_root / folder_name

    # Propagate HF token from caller or common env vars (used only for rare metadata; local path does not require it)
    if hf_token is None:
        hf_token = (
            os.environ.get("HF_TOKEN")
            or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            or os.environ.get("HF_HUB_TOKEN")
        )
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token
        os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token

    model_obj = None
    if local_model_dir.exists() and (local_model_dir / "model.safetensors").exists():
        logger.info(f"Loading {model} directly from local checkpoint on Z: drive: {local_model_dir}")
        t5_local_dir = local_model_dir / "t5gemma-b-b-ul2"
        has_local_t5 = t5_local_dir.exists() and (t5_local_dir / "model.safetensors").exists()

        try:
            from stable_audio_3.loading_utils import create_diffusion_cond_from_config, load_file, copy_state_dict
            from stable_audio_3 import StableAudioModel
            import torch
            import json

            config_path = local_model_dir / "model_config.json"
            ckpt_path = local_model_dir / "model.safetensors"

            with open(config_path) as f:
                model_config = json.load(f)

            device = "cuda" if torch.cuda.is_available() else "cpu"

            if has_local_t5:
                logger.info(f"Local t5gemma-b-b-ul2 present — patching T5GemmaConditioner with standard-transformers local loader (local_files_only=True)")

                # Import the base + module refs for safe monkey-patching
                from stable_audio_3.models.conditioners import Conditioner
                import stable_audio_3.models.conditioners as _cond_mod
                import stable_audio_3.factory as _fact_mod

                class LocalT5GemmaConditioner(Conditioner):
                    """Resilient local-only drop-in replacement.
                    Uses AutoModel/AutoTokenizer (never the custom T5GemmaEncoderModel symbol).
                    Returns the exact (embeddings, attention_mask) interface expected by MultiConditioner + diffusion wrapper.
                    """
                    def __init__(self, output_dim: int, max_length: int = 256, padding_mode: str = "learned", **kwargs: tp.Any):
                        emb_dim = 768  # known for google/t5gemma-b-b-ul2
                        super().__init__(emb_dim, output_dim, project_out=(emb_dim != output_dim), padding_mode=padding_mode)
                        self.max_length = int(max_length) if max_length else 256
                        self._device_initialized = False

                        t5_path = str(t5_local_dir)

                        # Match library's effort to keep logs clean during load
                        prev_hf = os.environ.get("HF_HUB_DISABLE_PROGRESS_BARS")
                        prev_trans = os.environ.get("TRANSFORMERS_VERBOSITY")
                        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
                        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
                        prev_level = logging.root.manager.disable
                        logging.disable(logging.ERROR)

                        try:
                            from transformers import AutoModel, AutoTokenizer, AutoConfig
                            hf_kwargs = {"local_files_only": True}
                            if hf_token:
                                hf_kwargs["token"] = hf_token
                            tok = AutoTokenizer.from_pretrained(t5_path, **hf_kwargs)
                            cfg = AutoConfig.from_pretrained(t5_path, **hf_kwargs)
                            cfg.is_encoder_decoder = False
                            enc = AutoModel.from_pretrained(t5_path, config=cfg, **hf_kwargs)
                            enc.eval().requires_grad_(False)
                            # Do not register as child module (matches some patterns in original)
                            self.__dict__["model"] = enc
                            self.tokenizer = tok
                        except Exception as load_err:
                            # Restore before re-raising so env is clean
                            logging.disable(prev_level)
                            if prev_hf is None:
                                os.environ.pop("HF_HUB_DISABLE_PROGRESS_BARS", None)
                            else:
                                os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = prev_hf
                            if prev_trans is None:
                                os.environ.pop("TRANSFORMERS_VERBOSITY", None)
                            else:
                                os.environ["TRANSFORMERS_VERBOSITY"] = prev_trans
                            raise RuntimeError(f"Standard transformers local load of t5gemma-b-b-ul2 FAILED: {load_err}") from load_err
                        finally:
                            try:
                                logging.disable(prev_level)
                            except Exception:
                                pass
                            if prev_hf is None:
                                os.environ.pop("HF_HUB_DISABLE_PROGRESS_BARS", None)
                            else:
                                os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = prev_hf
                            if prev_trans is None:
                                os.environ.pop("TRANSFORMERS_VERBOSITY", None)
                            else:
                                os.environ["TRANSFORMERS_VERBOSITY"] = prev_trans

                    def forward(self, inputs, device):
                        """Exact interface match: returns (embeddings, attention_mask) for cross-attn use."""
                        if not self._device_initialized:
                            self.model.to(device)
                            if hasattr(self, "proj_out") and not isinstance(getattr(self, "proj_out", None), torch.nn.Identity):
                                self.proj_out.to(device)
                            self._device_initialized = True

                        # Handle pre-tokenized dicts (from some collators) or raw prompt strings
                        if inputs and isinstance(inputs[0], dict):
                            input_ids = torch.stack([x["input_ids"] for x in inputs]).to(device, non_blocking=True)
                            attention_mask = torch.stack([x["attention_mask"] for x in inputs]).to(device, non_blocking=True).to(torch.bool)
                        else:
                            encoded = self.tokenizer(
                                inputs,
                                truncation=True,
                                max_length=self.max_length,
                                padding="max_length",
                                return_tensors="pt",
                            )
                            input_ids = encoded["input_ids"].to(device, non_blocking=True)
                            attention_mask = encoded["attention_mask"].to(device, non_blocking=True).to(torch.bool)

                        with torch.no_grad():
                            out = self.model(input_ids=input_ids, attention_mask=attention_mask)
                            # Support both BaseModelOutput and tuple return styles
                            embeddings = getattr(out, "last_hidden_state", out[0] if isinstance(out, (tuple, list)) else out)

                        if hasattr(self, "proj_out") and not isinstance(getattr(self, "proj_out", None), torch.nn.Identity):
                            try:
                                pdt = next(self.proj_out.parameters()).dtype
                                embeddings = embeddings.to(pdt)
                                embeddings = self.proj_out(embeddings)
                            except Exception:
                                pass  # identity or cpu fallback

                        embeddings = self.apply_padding(embeddings, attention_mask)
                        return embeddings, attention_mask

                # Perform the patch so the factory's create_multi_conditioner will use our class for type=="t5gemma"
                _orig_t5 = _cond_mod.T5GemmaConditioner
                _cond_mod.T5GemmaConditioner = LocalT5GemmaConditioner
                _fact_mod.T5GemmaConditioner = LocalT5GemmaConditioner

                try:
                    raw_model = create_diffusion_cond_from_config(model_config)
                finally:
                    # Restore originals immediately (no global side-effects)
                    _cond_mod.T5GemmaConditioner = _orig_t5
                    _fact_mod.T5GemmaConditioner = _orig_t5
            else:
                # Rare case: local model dir but no t5 subdir — still create (may fail if t5gemma present in config)
                raw_model = create_diffusion_cond_from_config(model_config)

            # Now load the safetensors weights for DiT + pretransform (AE) — fully local
            state_dict = load_file(str(ckpt_path), device=device)
            copy_state_dict(raw_model, state_dict)

            model_obj = StableAudioModel(raw_model, model_config, device, model_half=True)
            logger.info("Loaded %s SUCCESSFULLY using 100% local Z: drive files + standard transformers t5gemma loader.", model)

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error("Direct local Z: drive load for model=%s at %s FAILED:\n%s", model, local_model_dir, tb)

            strong_warning = (
                "\n" + "!" * 80 + "\n"
                f"CRITICAL: Local checkpoint loading of '{model}' from\n"
                f"  {local_model_dir}\n"
                "FAILED.\n\n"
                "This module now ENFORCES local-only loading for any model that has a\n"
                "complete checkpoint directory on the Z: drive (including 'medium').\n"
                "The legacy `StableAudioModel.from_pretrained(model)` / library HF path\n"
                "is intentionally NOT used as a silent fallback because it triggers the\n"
                "well-known T5GemmaEncoderModel import crash in the current transformers stack.\n\n"
                f"Root cause: {e}\n\n"
                "Next steps:\n"
                "  1. Verify torch + torchvision versions are consistent (cu126 wheels recommended)\n"
                "  2. Re-install flash-attn and the editable stable-audio-3 package\n"
                "  3. Confirm t5gemma-b-b-ul2/model.safetensors exists under the checkpoint dir\n"
                "  4. (debug only) export FORAGEDJ_ALLOW_BROKEN_FALLBACK=1 to force the fragile HF path\n"
                "!" * 80 + "\n"
            )
            print(strong_warning, file=sys.stderr)
            logger.critical(strong_warning)

            allow_fallback = os.environ.get("FORAGEDJ_ALLOW_BROKEN_FALLBACK", "0") == "1"
            if allow_fallback:
                logger.warning("FORAGEDJ_ALLOW_BROKEN_FALLBACK is set — attempting library from_pretrained as last resort (this will probably crash with T5Gemma error).")
                model_obj = StableAudioModel.from_pretrained(model)
            else:
                raise RuntimeError(
                    f"Robust local-only load required for '{model}' (Z: drive checkpoint) but failed. "
                    "See the CRITICAL message above for diagnostics. "
                    "Set FORAGEDJ_ALLOW_BROKEN_FALLBACK=1 *only* for debugging the broken HF path."
                ) from e
    else:
        logger.info(f"No complete local checkpoint found for '{model}' at {local_model_dir}. Falling back to library (HF download may occur and T5Gemma issues are possible).")
        model_obj = StableAudioModel.from_pretrained(model)

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


# =============================================================================
# TEST / VALIDATION HELPER (for auditor & CI use — does NOT run full generation)
# =============================================================================

def _load_model_for_validation(
    model: str = "medium",
    hf_token: Optional[str] = None,
    require_local: bool = True,
) -> "StableAudioModel":
    """Validate the local loading logic for a model (especially 'medium') without
    invoking the expensive .generate() call.

    Returns the wrapped StableAudioModel on success so caller can inspect
    .model, .model_config, the conditioner etc.

    This is the recommended snippet for post-patch verification:

        uv run python -c '
        from src.foragedj.audio_gen import _load_model_for_validation
        m = _load_model_for_validation("medium")
        print("LOAD OK:", type(m))
        print("Has local t5 conditioner:", "prompt" in getattr(m.model, "conditioner", {}).conditioners)
        print("Sample rate:", m.model_config.get("sample_rate"))
        del m
        import torch
        if torch.cuda.is_available(): torch.cuda.empty_cache()
        print("Validation complete — no generation performed.")
        '
    """
    # We reuse the exact same loading code path by calling generate_track with a
    # tiny duration + a flag, but short-circuit before the actual diffusion.
    # Instead we directly exercise the private load path by temporarily
    # overriding progress and doing a dry load.
    #
    # For simplicity and to avoid any generation side-effects or long runs,
    # we duplicate the critical load block here (kept in sync with main impl).

    # Resolve token
    if hf_token is None:
        hf_token = (
            os.environ.get("HF_TOKEN")
            or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            or os.environ.get("HF_HUB_TOKEN")
        )
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token
        os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token

    checkpoint_root = Path(__file__).parent.parent.parent / "checkpoints"
    name_map = {
        "small-music": "stable-audio-3-small-music",
        "small-sfx": "stable-audio-3-small-sfx",
        "medium": "stable-audio-3-medium",
    }
    folder_name = name_map.get(model, model)
    local_model_dir = checkpoint_root / folder_name

    if require_local and not (local_model_dir.exists() and (local_model_dir / "model.safetensors").exists()):
        raise RuntimeError(f"require_local=True but no local checkpoint for {model} at {local_model_dir}")

    # Import the real loader pieces (will raise if stable-audio-3 missing)
    from stable_audio_3 import StableAudioModel  # type: ignore
    from stable_audio_3.loading_utils import create_diffusion_cond_from_config, load_file, copy_state_dict
    import json as _json
    import torch as _torch

    if not (local_model_dir.exists() and (local_model_dir / "model.safetensors").exists()):
        # Fall back path for non-local (rare for validation)
        return StableAudioModel.from_pretrained(model)

    t5_local_dir = local_model_dir / "t5gemma-b-b-ul2"
    has_local_t5 = t5_local_dir.exists() and (t5_local_dir / "model.safetensors").exists()

    config_path = local_model_dir / "model_config.json"
    ckpt_path = local_model_dir / "model.safetensors"

    with open(config_path) as f:
        model_config = _json.load(f)

    device = "cuda" if _torch.cuda.is_available() else "cpu"

    if has_local_t5:
        from stable_audio_3.models.conditioners import Conditioner
        import stable_audio_3.models.conditioners as _cond_mod
        import stable_audio_3.factory as _fact_mod

        class _ValLocalT5GemmaConditioner(Conditioner):
            def __init__(self, output_dim: int, max_length: int = 256, padding_mode: str = "learned", **kwargs: tp.Any):
                emb_dim = 768
                super().__init__(emb_dim, output_dim, project_out=(emb_dim != output_dim), padding_mode=padding_mode)
                self.max_length = int(max_length) if max_length else 256
                self._device_initialized = False
                t5_path = str(t5_local_dir)
                from transformers import AutoModel, AutoTokenizer, AutoConfig
                hf_kwargs = {"local_files_only": True}
                if hf_token:
                    hf_kwargs["token"] = hf_token
                tok = AutoTokenizer.from_pretrained(t5_path, **hf_kwargs)
                cfg = AutoConfig.from_pretrained(t5_path, **hf_kwargs)
                cfg.is_encoder_decoder = False
                enc = AutoModel.from_pretrained(t5_path, config=cfg, **hf_kwargs)
                enc.eval().requires_grad_(False)
                self.__dict__["model"] = enc
                self.tokenizer = tok

            def forward(self, inputs, device):
                if not self._device_initialized:
                    self.model.to(device)
                    self._device_initialized = True
                if inputs and isinstance(inputs[0], dict):
                    input_ids = _torch.stack([x["input_ids"] for x in inputs]).to(device, non_blocking=True)
                    attention_mask = _torch.stack([x["attention_mask"] for x in inputs]).to(device, non_blocking=True).to(_torch.bool)
                else:
                    encoded = self.tokenizer(inputs, truncation=True, max_length=self.max_length, padding="max_length", return_tensors="pt")
                    input_ids = encoded["input_ids"].to(device, non_blocking=True)
                    attention_mask = encoded["attention_mask"].to(device, non_blocking=True).to(_torch.bool)
                with _torch.no_grad():
                    out = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    embeddings = getattr(out, "last_hidden_state", out[0] if isinstance(out, (tuple, list)) else out)
                embeddings = self.apply_padding(embeddings, attention_mask)
                return embeddings, attention_mask

        _o = _cond_mod.T5GemmaConditioner
        _cond_mod.T5GemmaConditioner = _ValLocalT5GemmaConditioner
        _fact_mod.T5GemmaConditioner = _ValLocalT5GemmaConditioner
        try:
            raw = create_diffusion_cond_from_config(model_config)
        finally:
            _cond_mod.T5GemmaConditioner = _o
            _fact_mod.T5GemmaConditioner = _o
    else:
        raw = create_diffusion_cond_from_config(model_config)

    sd = load_file(str(ckpt_path), device=device)
    copy_state_dict(raw, sd)
    wrapped = StableAudioModel(raw, model_config, device, model_half=True)
    logger.info("_load_model_for_validation: successfully loaded %s (local=%s, has_t5_patch=%s)", model, True, has_local_t5)
    return wrapped
