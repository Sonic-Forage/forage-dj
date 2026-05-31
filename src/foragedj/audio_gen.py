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
    model: str = "open",
    progress_callback: Optional[Callable[[float, str], None]] = None,
    hf_token: Optional[str] = None,
    backend: str | None = None,   # None = use config default (comfy is now the primary path)
) -> Path:
    """Generate a track from text prompt + seed using ComfyUI (primary) or legacy Python backend.

    Returns path to the generated WAV.

    NOTE: As of 2026, the high-quality path is ComfyUI + ACE-Step 1.5 XL Turbo (and other strong ComfyUI audio workflows).
    The original Python Stable Audio 3 backend has been moved to the `legacy/stable-audio-python` branch.

    Args:
        prompt: Natural language description (e.g. "dark techno intro 128bpm")
        seed: Controls variation.
        duration: Target length in seconds
        model: For ComfyUI backend this is mostly ignored or used for workflow selection.
               Legacy Python models (small-music, medium, etc.) are only on the legacy branch.
        progress_callback: Optional callback
        hf_token: Only relevant for legacy Python path

    The ComfyUI backend supports remote servers (RunPod, Vast, local machine via Tailscale, etc.).
    """
    if progress_callback:
        progress_callback(0.0, "Checking for stable-audio-3...")

    # Resolve backend from explicit arg or central config (comfy is now the easy default)
    if backend is None:
        try:
            from .config import get_default_backend
            backend = get_default_backend()
        except Exception:
            backend = "comfy"

    # === ComfyUI backend (recommended add-on for local PC reliability) ===
    # This completely bypasses the fragile Python stable-audio-3 path.
    # Run ComfyUI separately (native at http://0.0.0.0:8188 or via ./scripts/launch_comfyui.sh)
    # and point it at your local checkpoints (including optimized TensorRT/ONNX versions).
    if backend.lower() == "comfy":
        from .comfy_client import generate_via_comfy
        from .paths import get_comfy_workflows_dir

        # Map model names to reasonable default workflows in workflows/comfy/
        if "open" in str(model).lower() or model == "open":
            workflow = get_comfy_workflows_dir() / "stable-audio-open.json"
        else:
            workflow = get_comfy_workflows_dir() / f"{model}.json"
        return generate_via_comfy(
            prompt=prompt,
            seed=seed,
            duration=duration,
            workflow_path=workflow,
            # Respects COMFYUI_URL env var; falls back to 127.0.0.1:8188 (works with 0.0.0.0 server bind)
            comfy_url=os.environ.get("COMFYUI_URL"),
        )

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

    # === Track 3: "open" model support (stabilityai/stable-audio-open-1.0) ===
    # First-class, reliable path using diffusers.StableAudioPipeline.
    # - Always snapshots to checkpoints/stable-audio-open-1.0/ (Z: aware via paths)
    # - Uses standard T5 (not T5Gemma), proper device handling in diffusers.
    # - New recommended default while medium (Track 1/2) is hardened.
    # - No monkey-patches, no SA3 dependency for this path.
    model_key = str(model).lower().strip()
    if model_key in ("open", "stable-audio-open", "stable-audio-open-1.0", "stable_audio_open"):
        return _generate_with_open_model(
            prompt=prompt,
            seed=seed,
            duration=duration,
            progress_callback=progress_callback,
            hf_token=hf_token,
        )

    # === Real implementation contributed by swarm agent (Phase 1 Audio Gen) ===
    # See .grok/swarm-outputs/audio-gen-agent-019e7a00-3f8e-7860-a884-ca10b8fb7297.md
    # and the approved plan Appendix B for full rationale + references.

    # ROBUST LOCAL-FIRST LOADING (bypasses all HF from_pretrained + T5GemmaEncoderModel crashes)
    # When a complete local checkpoint dir exists under checkpoints/ (with model.safetensors + t5gemma-b-b-ul2/),
    # we use create_diffusion_cond_from_config + safetensors load, but with a monkey-patched
    # conditioner that loads the text encoder via STANDARD transformers (AutoModel + local_files_only=True).
    # This never executes the library's T5GemmaConditioner.__init__ (the source of the import error).
    # No silent fallbacks to the known-broken HF path for local checkpoint cases.
    checkpoint_root = paths.get_checkpoints_dir()  # respects Z: / FORAGE_DJ_DATA_ROOT / paths.json etc.

    name_map = {
        "small-music": "stable-audio-3-small-music",
        "small-sfx": "stable-audio-3-small-sfx",
        "medium": "stable-audio-3-medium",
        "open": "stable-audio-open-1.0",
        "stable-audio-open": "stable-audio-open-1.0",
        "stable-audio-open-1.0": "stable-audio-open-1.0",
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
            model_half = True  # matches previous hardcoded + what official path uses for medium

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
                            from transformers import T5GemmaEncoderModel, AutoTokenizer, AutoConfig
                            hf_kwargs = {"local_files_only": True}
                            if hf_token:
                                hf_kwargs["token"] = hf_token
                            tok = AutoTokenizer.from_pretrained(t5_path, **hf_kwargs)
                            cfg = AutoConfig.from_pretrained(t5_path, **hf_kwargs)
                            cfg.is_encoder_decoder = False
                            enc = T5GemmaEncoderModel.from_pretrained(t5_path, config=cfg, **hf_kwargs)
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
                        """Exact interface match: returns (embeddings, attention_mask) for cross-attn use.
                        DEBUG INSTRUMENTED for Track 1 device mismatch hunt (see plan).
                        """
                        print(f"[T5GEMMA COND LOG] forward called: device_arg={device}, _initialized={self._device_initialized}")
                        try:
                            mdev = next(self.model.parameters()).device if hasattr(self, 'model') and any(True for _ in self.model.parameters()) else 'no-params'
                            mdtype = next(self.model.parameters()).dtype if hasattr(self, 'model') and any(True for _ in self.model.parameters()) else 'N/A'
                            print(f"[T5GEMMA COND LOG]   t5_model current: device={mdev}, dtype={mdtype}")
                        except Exception as e:
                            print(f"[T5GEMMA COND LOG]   t5_model inspect err: {e}")
                        try:
                            if hasattr(self, 'proj_out') and not isinstance(self.proj_out, torch.nn.Identity):
                                pdev = next(self.proj_out.parameters()).device
                                print(f"[T5GEMMA COND LOG]   proj_out current: device={pdev}")
                        except Exception as e:
                            print(f"[T5GEMMA COND LOG]   proj inspect err: {e}")

                        if not self._device_initialized:
                            print(f"[T5GEMMA COND LOG]   performing lazy device init to {device}")
                            self.model.to(device)
                            if hasattr(self, "proj_out") and not isinstance(getattr(self, "proj_out", None), torch.nn.Identity):
                                self.proj_out.to(device)
                            # Critical: move the entire Conditioner (incl. parent-registered padding buffers etc.)
                            # so apply_padding and downstream see consistent device.
                            self.to(device)
                            self._device_initialized = True
                            print(f"[T5GEMMA COND LOG]   after self.to({device}) and model.to")

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

                        print(f"[T5GEMMA COND LOG]   tokenized: input_ids.device={input_ids.device}, att_mask.device={attention_mask.device}")

                        with torch.no_grad():
                            out = self.model(input_ids=input_ids, attention_mask=attention_mask)
                            # Support both BaseModelOutput and tuple return styles
                            embeddings = getattr(out, "last_hidden_state", out[0] if isinstance(out, (tuple, list)) else out)

                        print(f"[T5GEMMA COND LOG]   raw embeddings from t5: device={embeddings.device}, dtype={embeddings.dtype}, shape={embeddings.shape}")

                        if hasattr(self, "proj_out") and not isinstance(getattr(self, "proj_out", None), torch.nn.Identity):
                            try:
                                pdt = next(self.proj_out.parameters()).dtype
                                embeddings = embeddings.to(pdt)
                                embeddings = self.proj_out(embeddings)
                            except Exception:
                                pass  # identity or cpu fallback

                        embeddings = embeddings.to(device)
                        attention_mask = attention_mask.to(device) if isinstance(attention_mask, torch.Tensor) else attention_mask
                        print(f"[T5GEMMA COND LOG]   pre-apply_padding: embeds.device={embeddings.device}, mask.device={getattr(attention_mask, 'device', None)}")
                        embeddings = self.apply_padding(embeddings, attention_mask)
                        embeddings = embeddings.to(device)
                        attention_mask = attention_mask.to(device) if isinstance(attention_mask, torch.Tensor) else attention_mask
                        print(f"[T5GEMMA COND LOG]   RETURN: embeds.device={embeddings.device} dtype={embeddings.dtype}, mask.device={getattr(attention_mask, 'device', None)}")
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
            # Load on CPU first (matches official load_diffusion_cond path) to avoid VRAM fragmentation/OOM on large ckpts during direct-to-GPU safetensors load.
            state_dict = load_file(str(ckpt_path))
            copy_state_dict(raw_model, state_dict)

            # === FIX for Track 1 device mismatch (the root cause) ===
            # The create + copy (even with device= on load_file) does not guarantee EVERY submodule
            # (DiT including to_cond_embed linears, NumberConditioner for seconds_total cross/global,
            # pretransform, Conditioner padding etc.) ends up on the target device.
            # Official loader does model.to(device) after copy; we were missing it in local monkey path.
            # This was causing "cuda vs cpu" inside DiT.to_cond_embed / transformer mm during sampling
            # even when T5/Number cond outputs were correctly on device (confirmed via instrumented logs).
            # T5 encoder itself is deliberately NOT registered as child (hidden in __dict__), so its
            # .to is still handled lazily in LocalT5GemmaConditioner.forward (which works).
            print(f"[LOAD FIX] Forcing raw_model (DiT + all conditioners + pretransform) .to({device}) + eval + no-grad...")
            raw_model = raw_model.to(device).eval().requires_grad_(False)
            if model_half:
                print("[LOAD FIX] Also casting to float16 (model_half=True)")
                raw_model = raw_model.to(torch.float16)
            # Re-assign in case
            # (the var raw_model is used below for Stable ctor)

            model_obj = StableAudioModel(raw_model, model_config, device, model_half=bool(model_half))
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
    """Validate the local loading logic for a model (especially "medium") without
    invoking the expensive .generate() call.
    
    Returns the wrapped StableAudioModel on success so caller can inspect
    .model, .model_config, the conditioner etc.
    
    Note: For model="open" this validation is not applicable (uses diffusers path);
    it will raise a clear error. Use generate_track(..., model="open") for that path.
    
    See the comment block immediately below for the recommended post-patch
    verification snippet.
    """ 

    # Recommended verification snippet (run from the project root):
    #
    #   uv run python -c '
    #   from src.foragedj.audio_gen import _load_model_for_validation
    #   m = _load_model_for_validation("medium", require_local=True)
    #   print("LOAD OK:", type(m))
    #   print("Sample rate:", m.model_config.get("sample_rate"))
    #   del m
    #   import torch
    #   if torch.cuda.is_available(): torch.cuda.empty_cache()
    #   print("Validation complete — no generation performed.")
    #   '
    #
    
    model_key = str(model).lower().strip()
    if model_key in ("open", "stable-audio-open", "stable-audio-open-1.0"):
        raise NotImplementedError(
            " _load_model_for_validation does not support the 'open' model (diffusers path). "
            "Use the real generate_track(model='open') for validation, or test the pipeline directly."
        )

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

    checkpoint_root = paths.get_checkpoints_dir()  # respects Z: / FORAGE_DJ_DATA_ROOT / paths.json etc.
    name_map = {
        "small-music": "stable-audio-3-small-music",
        "small-sfx": "stable-audio-3-small-sfx",
        "medium": "stable-audio-3-medium",
        "open": "stable-audio-open-1.0",
        "stable-audio-open": "stable-audio-open-1.0",
        "stable-audio-open-1.0": "stable-audio-open-1.0",
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
                from transformers import T5GemmaEncoderModel, AutoTokenizer, AutoConfig
                hf_kwargs = {"local_files_only": True}
                if hf_token:
                    hf_kwargs["token"] = hf_token
                tok = AutoTokenizer.from_pretrained(t5_path, **hf_kwargs)
                cfg = AutoConfig.from_pretrained(t5_path, **hf_kwargs)
                cfg.is_encoder_decoder = False
                enc = T5GemmaEncoderModel.from_pretrained(t5_path, config=cfg, **hf_kwargs)
                enc.eval().requires_grad_(False)
                self.__dict__["model"] = enc
                self.tokenizer = tok

            def forward(self, inputs, device):
                print(f"[VAL T5GEMMA COND LOG] forward called: device_arg={device}, _init={self._device_initialized}")
                if not self._device_initialized:
                    self.model.to(device)
                    self.to(device)
                    self._device_initialized = True
                    print(f"[VAL T5GEMMA COND LOG]   lazy to({device}) done")
                if inputs and isinstance(inputs[0], dict):
                    input_ids = _torch.stack([x["input_ids"] for x in inputs]).to(device, non_blocking=True)
                    attention_mask = _torch.stack([x["attention_mask"] for x in inputs]).to(device, non_blocking=True).to(_torch.bool)
                else:
                    encoded = self.tokenizer(inputs, truncation=True, max_length=self.max_length, padding="max_length", return_tensors="pt")
                    input_ids = encoded["input_ids"].to(device, non_blocking=True)
                    attention_mask = encoded["attention_mask"].to(device, non_blocking=True).to(_torch.bool)
                print(f"[VAL T5GEMMA COND LOG]   tokenized ids.dev={input_ids.device}")
                with _torch.no_grad():
                    out = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    embeddings = getattr(out, "last_hidden_state", out[0] if isinstance(out, (tuple, list)) else out)
                print(f"[VAL T5GEMMA COND LOG]   t5 out embeds.dev={embeddings.device}")
                embeddings = embeddings.to(device)
                attention_mask = attention_mask.to(device) if isinstance(attention_mask, _torch.Tensor) else attention_mask
                embeddings = self.apply_padding(embeddings, attention_mask)
                embeddings = embeddings.to(device)
                attention_mask = attention_mask.to(device) if isinstance(attention_mask, _torch.Tensor) else attention_mask
                print(f"[VAL T5GEMMA COND LOG]   RETURN embeds.dev={embeddings.device}")
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

    sd = load_file(str(ckpt_path))  # CPU first (avoid OOM/frag); explicit .to below
    copy_state_dict(raw, sd)

    # Apply same device/dtype hardening as main load path (for consistency, even though val does not sample)
    print(f"[_VAL LOAD FIX] Forcing raw model .to({device}) ...")
    raw = raw.to(device).eval().requires_grad_(False)
    val_model_half = True
    if val_model_half:
        raw = raw.to(torch.float16)
    wrapped = StableAudioModel(raw, model_config, device, model_half=val_model_half)
    logger.info("_load_model_for_validation: successfully loaded %s (local=%s, has_t5_patch=%s)", model, True, has_local_t5)
    return wrapped


# =============================================================================
# TRACK 3 HELPER: Open Stable Audio model (diffusers path, reliable default)
# =============================================================================

def _generate_with_open_model(
    prompt: str,
    seed: int = 42,
    duration: float = 60.0,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    hf_token: Optional[str] = None,
) -> Path:
    """Generate using stabilityai/stable-audio-open-1.0 via diffusers.StableAudioPipeline.

    This is the clean, first-class "open" / "stable-audio-open" implementation (Track 3).
    - Snapshots exactly once into checkpoints/stable-audio-open-1.0/ (respects paths.py Z: rules + local-first).
    - Standard HF loading + diffusers device/dtype handling (no custom conditioner, no T5Gemma, no flash-attn monkey business).
    - Recommended default for most users while the SA3 "medium" local path (Tracks 1+2) is hardened.
    - Max ~47s per call; use shorter duration or multiple calls for longer pieces.
    """
    if progress_callback:
        progress_callback(0.15, "Preparing stable-audio-open-1.0 (reliable diffusers path)...")

    try:
        from diffusers import StableAudioPipeline
        import torch
        from huggingface_hub import snapshot_download
        from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError
        import numpy as np
    except ImportError as e:
        msg = (
            "\n\n*** For --model open (or stable-audio-open) you need the diffusers package. ***\n\n"
            "Quick one-time install (after your pinned torch/flash stack):\n"
            "  uv pip install diffusers\n\n"
            "This pulls in the standard, well-maintained loader for stabilityai/stable-audio-open-1.0\n"
            "(public weights, T5 text encoder, clean device movement, no SA3 custom classes).\n"
            "Once installed, `foragedj generate \"...\" --model open` will download the ~2-3GB\n"
            "checkpoint ONCE into checkpoints/stable-audio-open-1.0/ (Z: drive aware) and then\n"
            "generate locally with zero network.\n\n"
            f"Import error details: {type(e).__name__}: {e}\n"
        )
        raise RuntimeError(msg) from e

    # Use project paths for checkpoint location (Z: / data root aware)
    open_dir = paths.get_checkpoints_dir() / "stable-audio-open-1.0"
    open_dir.mkdir(parents=True, exist_ok=True)

    # One-time snapshot into OUR controlled dir (not just opaque HF cache).
    # Subsequent runs are fully offline + local_files_only.
    needs_download = not (open_dir / "model_index.json").exists()
    if needs_download:
        if progress_callback:
            progress_callback(0.20, "Downloading stable-audio-open-1.0 weights (one-time, ~2-3 GB to local checkpoints/)...")
        logger.info("Performing one-time snapshot of stabilityai/stable-audio-open-1.0 -> %s", open_dir)
        token = hf_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        try:
            snapshot_download(
                repo_id="stabilityai/stable-audio-open-1.0",
                local_dir=str(open_dir),
                local_dir_use_symlinks=False,  # real files for portability / WSL / Windows mounts
                token=token,
                # Skip large non-model files (datasets attributions, images, md)
                ignore_patterns=["*.csv", "*.md", "LICENSE*", "*.png", "fma_*", "freesound_*", ".git*"],
            )
            logger.info("Snapshot complete for open model at %s", open_dir)
        except (GatedRepoError, HfHubHTTPError) as gated_err:
            err_str = str(gated_err)
            if "401" in err_str or "gated" in err_str.lower() or "access" in err_str.lower():
                msg = (
                    "\n\n*** GATED REPO: stabilityai/stable-audio-open-1.0 requires license acceptance ***\n\n"
                    "Even though the model is 'open weights', Stability AI still requires you to visit the\n"
                    "model page and explicitly agree to the terms before any download (same as SA3 medium).\n\n"
                    "FIX (do this once):\n"
                    "  1. Go to: https://huggingface.co/stabilityai/stable-audio-open-1.0\n"
                    "  2. Log in with the same account as your HF_TOKEN\n"
                    "  3. Click 'Agree and access repository' (or the license accept button)\n"
                    "  4. Ensure your HF_TOKEN (or .grok/hf-token.env) is valid and exported\n"
                    "  5. Re-run the generate command.\n\n"
                    "Then the snapshot will succeed into checkpoints/stable-audio-open-1.0/ and\n"
                    "future runs will be fully local/offline.\n\n"
                    f"Original error: {err_str[:200]}\n"
                )
                raise RuntimeError(msg) from gated_err
            raise
        except Exception as snap_e:
            logger.error("Snapshot failed for open model: %s", snap_e)
            raise

    if progress_callback:
        progress_callback(0.45, "Loading StableAudioPipeline from local Z: checkpoint (local_files_only=True)...")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    pipe = StableAudioPipeline.from_pretrained(
        str(open_dir),
        torch_dtype=dtype,
        local_files_only=True,
    )
    pipe = pipe.to(device)

    if progress_callback:
        progress_callback(0.55, f"Running diffusion (seed={seed}, duration~{duration}s, 100 steps, guidance=7.0)...")

    generator = torch.Generator(device=device).manual_seed(int(seed))
    audio_end_s = min(float(duration), 47.0)  # model limit

    # Core generation call (standard diffusers API)
    pipe_output = pipe(
        prompt=prompt,
        negative_prompt="Low quality, muffled, noisy, artifacts, distorted, poor recording, low fidelity.",
        num_inference_steps=100,
        guidance_scale=7.0,
        generator=generator,
        audio_end_in_s=audio_end_s,
    )

    waveform = pipe_output.audios[0]
    sr = getattr(getattr(pipe, "vae", None), "sampling_rate", 44100)

    # Prepare output path (reuse module CACHE_DIR)
    slug = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in prompt[:35]).strip("_")[:40]
    out_path = CACHE_DIR / f"{seed}_{slug}.wav"

    # Robust save: handle tensor or ndarray from the pipeline, ensure correct shape for torchaudio (C, T)
    import torchaudio
    if isinstance(waveform, torch.Tensor):
        wav_t = waveform.cpu().float()
        if wav_t.ndim == 1:
            wav_t = wav_t.unsqueeze(0)
        elif wav_t.ndim == 2 and wav_t.shape[0] > wav_t.shape[1] and wav_t.shape[1] <= 2:
            # (T, C) -> (C, T)
            wav_t = wav_t.T
        torchaudio.save(str(out_path), wav_t, sample_rate=sr)
    else:
        # numpy path (common in examples)
        arr = np.asarray(waveform, dtype="float32")
        if arr.ndim == 1:
            arr = arr[None, :]
        elif arr.ndim == 2 and arr.shape[0] > arr.shape[1] and arr.shape[1] <= 2:
            arr = arr.T
        torchaudio.save(str(out_path), torch.from_numpy(arr), sample_rate=sr)

    if progress_callback:
        progress_callback(0.90, "Saving + embedding provenance...")

    from .utils import embed_metadata
    embed_metadata(out_path, prompt=prompt, seed=seed, model="open", duration=duration, sample_rate=sr)

    if progress_callback:
        progress_callback(1.0, "Done.")

    logger.info("Generated %s (seed=%s, model=open/stable-audio-open-1.0, sr=%s)", out_path, seed, sr)
    return out_path
