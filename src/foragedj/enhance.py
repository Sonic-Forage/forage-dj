"""Audio enhancement, super-resolution, voice cleaning, and TTS tools.

Part of the 2025 Sonic Forage enhancement stack:
- FlashSR (tiny + one-step) for fast 16k→48kHz upscaling + clarity
- AudioSR (drbaph) for highest-quality diffusion-based enhancement
- LocalVQE for real-time CPU voice (AEC + noise + reverb removal)
- Kokoro-82M for lightweight high-quality TTS / vocal elements
- Demucs (via optional stems extra) for stem separation

All paths respect the Z: drive layout (checkpoints/enhancers/, checkpoints/voice/).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .config import load_config

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
ENHANCERS_DIR = PROJECT_ROOT / "checkpoints" / "enhancers"
VOICE_DIR = PROJECT_ROOT / "checkpoints" / "voice"


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def enhance_audio(
    input_path: str | Path,
    output_path: Optional[str | Path] = None,
    model: str = "flashsr-tiny",
    device: str = "cuda",
) -> Path:
    """
    Upscale + enhance audio using the best practical model for the job.

    model choices:
      - "flashsr-tiny"   : 200-400x realtime, tiny (default, great for live/batch)
      - "flashsr-onestep": 2025 one-step distilled (best quality/speed tradeoff)
      - "audiosr"        : highest perceptual quality (slow, needs GPU + steps)

    Returns path to enhanced 48kHz file.
    """
    input_path = Path(input_path).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    if output_path is None:
        out_dir = PROJECT_ROOT / "test_outputs" / "enhanced"
        _ensure_dir(out_dir)
        output_path = out_dir / f"{input_path.stem}_enhanced_48k.wav"
    output_path = Path(output_path)
    _ensure_dir(output_path.parent)

    print(f"🔊 Enhancing: {input_path} → {output_path}")
    print(f"   Model: {model} (device={device})")

    if model == "flashsr-tiny":
        # The tiny variant is extremely small. Real inference lives in the FlashSR github
        # or ONNX export. For now we give a clear actionable path + copy the file as placeholder.
        model_dir = ENHANCERS_DIR / "flashsr-tiny"
        print(f"   Model dir: {model_dir}")
        if not model_dir.exists() or not any(model_dir.iterdir()):
            print("   ⚠️  flashsr-tiny not fully downloaded. Run:")
            print("      uv run python scripts/download_checkpoints.py --group enhancers")
            print("   Then see https://github.com/ysharma3501/FlashSR for the tiny inference code / ONNX.")
        # Placeholder behavior (real wrapper can load the small net + run here later)
        # For immediate usefulness we just copy + note the real step.
        import shutil
        shutil.copy2(input_path, output_path)
        print("   (Placeholder copy created. Replace with real FlashSR tiny call when weights + small inference ready.)")
        print("   Recommended: git clone the FlashSR repo + use their ONNX or torch path for instant 48k magic.")

    elif model == "flashsr-onestep":
        model_dir = ENHANCERS_DIR / "flashsr-onestep"
        print(f"   Using laion one-step FlashSR from {model_dir}")
        print("   See enhance.py in that repo (standalone, needs torch + scipy + soundfile).")
        print("   Run their enhance.py on the input for excellent one-pass 48k results.")
        import shutil
        shutil.copy2(input_path, output_path)  # placeholder

    elif model == "audiosr":
        model_dir = ENHANCERS_DIR / "audiosr"
        print(f"   AudioSR (drbaph) at {model_dir}")
        print("   Best used via ComfyUI-AudioSR node or the original versatile_audio_super_resolution repo.")
        print("   Two checkpoints: audiosr_basic_fp32.safetensors (music/general) and _speech_ variant.")
        import shutil
        shutil.copy2(input_path, output_path)

    else:
        raise ValueError(f"Unknown enhancer model: {model}")

    print(f"✅ Enhancement step complete (see notes above for full inference): {output_path}")
    return output_path


def clean_voice(
    mic_path: str | Path,
    ref_path: Optional[str | Path] = None,
    output_path: Optional[str | Path] = None,
) -> Path:
    """
    Real-time voice quality enhancement using LocalVQE.

    Removes echo (AEC), background noise, and reverb in a single causal pass.
    Extremely lightweight — runs 5-10x realtime on CPU.

    For maximum speed: build the GGML C++ engine from https://github.com/localai-org/LocalVQE
    GGUF weights live in checkpoints/voice/localvqe/
    (Windows: needs Visual Studio Build Tools + cmake; Linux is easier with the nix flake)
    """
    mic_path = Path(mic_path).expanduser().resolve()
    if not mic_path.exists():
        raise FileNotFoundError(mic_path)

    vqe_dir = VOICE_DIR / "localvqe"
    gguf = vqe_dir / "localvqe-v1.3-4.8M-f32.gguf"
    if not gguf.exists():
        gguf = vqe_dir / "localvqe-v1.2-1.3M-f32.gguf"

    if output_path is None:
        out_dir = PROJECT_ROOT / "test_outputs" / "cleaned"
        _ensure_dir(out_dir)
        output_path = out_dir / f"{mic_path.stem}_clean.wav"
    output_path = Path(output_path)
    _ensure_dir(output_path.parent)

    print(f"🗣️  Cleaning voice: {mic_path}")
    print(f"   LocalVQE weights: {gguf if gguf.exists() else 'NOT FOUND — run download-models --group voice'}")

    if ref_path:
        print(f"   Reference (far-end for AEC): {ref_path}")

    # Best path: the compiled localvqe binary from their repo
    # Fallback: PyTorch reference (slower)
    if gguf.exists():
        print("   → Use the C++ binary for real-time: ./ggml/build/bin/localvqe ...")
        print("     (Build instructions in the LocalVQE GitHub + docs/ENHANCEMENT_TOOLS.md)")
    else:
        print("   No GGUF found yet. Download with: uv run python scripts/download_checkpoints.py --group voice")

    # Placeholder for now (real call wires to the binary or torch reference)
    import shutil
    shutil.copy2(mic_path, output_path)
    print(f"   (Cleaned placeholder written — wire the real LocalVQE binary for production use)")
    return output_path


def text_to_speech(
    text: str,
    voice: str = "af_heart",
    output_path: Optional[str | Path] = None,
    lang: str = "a",
) -> Path:
    """
    High-quality lightweight TTS using Kokoro-82M (Apache 2.0, 82M params, streaming capable).

    Many voices available — see https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md

    Requires (one time):
        uv pip install kokoro soundfile
        # Linux:   sudo apt install espeak-ng
        # Windows: eSpeak NG .msi from https://github.com/espeak-ng/espeak-ng/releases
    """
    if output_path is None:
        out_dir = PROJECT_ROOT / "test_outputs" / "tts"
        _ensure_dir(out_dir)
        safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in text[:40])
        output_path = out_dir / f"kokoro_{safe}.wav"
    output_path = Path(output_path)
    _ensure_dir(output_path.parent)

    try:
        from kokoro import KPipeline  # type: ignore
        import soundfile as sf  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "Kokoro TTS requires: uv pip install kokoro soundfile\n"
            "Linux:   sudo apt install espeak-ng\n"
            "Windows: Download the eSpeak NG .msi from https://github.com/espeak-ng/espeak-ng/releases\n"
            f"Original error: {e}"
        ) from None

    print(f"🗣️  Kokoro TTS → {voice} : {text[:80]}{'...' if len(text) > 80 else ''}")
    pipeline = KPipeline(lang_code=lang)

    audio_chunks = []
    for gs, ps, audio in pipeline(text, voice=voice):
        print(f"   phonemes: {ps[:60]}{'...' if len(ps) > 60 else ''}")
        audio_chunks.append(audio)

    if audio_chunks:
        import numpy as np
        full = np.concatenate(audio_chunks)
        sf.write(str(output_path), full, 24000)
        print(f"✅ Saved: {output_path}  (24kHz)")
        return output_path
    else:
        raise RuntimeError("Kokoro produced no audio")


def split_stems(
    input_path: str | Path,
    output_dir: Optional[str | Path] = None,
    model: str = "htdemucs",
) -> Path:
    """
    Source separation using Demucs (or RoFormer variants via audio-separator).

    Requires the optional extra:
        uv sync --extra stems

    Outputs vocals.wav, drums.wav, bass.wav, other.wav (or 6-stem variants).
    """
    input_path = Path(input_path).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    if output_dir is None:
        output_dir = PROJECT_ROOT / "test_outputs" / "stems" / input_path.stem
    output_dir = Path(output_dir)
    _ensure_dir(output_dir)

    try:
        import demucs  # noqa: F401
    except ImportError:
        raise RuntimeError(
            "Stem separation requires the 'stems' extra: uv sync --extra stems\n"
            "Then: demucs --two-stems=vocals your_track.wav"
        ) from None

    print(f"✂️  Splitting stems: {input_path} → {output_dir}")
    # Use the demucs CLI for reliability (it knows all its models)
    cmd = [
        sys.executable, "-m", "demucs",
        "--out", str(output_dir.parent),
        "--name", model,
        str(input_path),
    ]
    print("   Running:", " ".join(cmd))
    subprocess.check_call(cmd)
    print(f"✅ Stems written under: {output_dir.parent / model}")
    return output_dir


if __name__ == "__main__":
    print("forage-dj enhance module. Use via CLI: foragedj enhance / foragedj speak etc.")