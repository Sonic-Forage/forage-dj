"""Shared utilities: config, logging bootstrap, metadata embedding, paths.

All generated content must carry the harm-reduction safety note.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__

logger = logging.getLogger(__name__)

SAFETY_NOTE = (
    "Public-safe rave tool — harm reduction first. "
    "forage-dj v" + __version__ + ". Prompt provenance required."
)

CONFIG_DIR = Path.home() / ".foragedj"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

GENERATED_DIR = CONFIG_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

MIDI_MAP_PATH = CONFIG_DIR / "midi_mappings.json"


def setup_logging(level: int = logging.INFO) -> None:
    """Idempotent logging config suitable for CLI + GUI."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def embed_metadata(path: Path, prompt: str, seed: int, model: str, **extra: Any) -> None:
    """Write a companion JSON sidecar with full provenance + safety note.

    Later: also embed in WAV RIFF INFO / ID3 tags when the real generator lands.
    """
    meta = {
        "prompt": prompt,
        "seed": seed,
        "model": model,
        "safety_note": SAFETY_NOTE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "forage_dj_version": __version__,
        **extra,
    }
    sidecar = path.with_suffix(path.suffix + ".json")
    sidecar.write_text(json.dumps(meta, indent=2))
    logger.debug("Wrote provenance sidecar: %s", sidecar)


def load_config() -> dict:
    cfg_path = CONFIG_DIR / "config.json"
    if cfg_path.exists():
        return json.loads(cfg_path.read_text())
    return {"default_seed": 42, "default_duration": 60.0}


def tag_wav_for_dj(path: Path, title: str = "", artist: str = "forage-dj", 
                   bpm: float = 0.0, key: str = "", camelot: str = "", 
                   comment: str = "") -> Path:
    """
    Make a WAV file DJ-app friendly:
    - Renames it to a standard format: NN_Title_BPM_Key.wav (e.g. 01_Bassline_128BPM_8A.wav)
    - Writes rich sidecar JSON with full info (prompt, seed, safety, etc.)
    
    This is what users expect when loading folders into Serato, Rekordbox, Traktor, Engine DJ, etc.
    """
    from . import analysis

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    # Auto-analyze if BPM/Key not provided
    if bpm <= 0 or not key:
        try:
            res = analysis.detect_bpm_key(path)
            bpm = res.bpm
            key = res.key
            camelot = res.camelot
        except Exception:
            pass

    # Build nice filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:40].strip("_")
    if not safe_title:
        safe_title = path.stem

    bpm_str = f"{int(bpm)}BPM" if bpm > 0 else ""
    key_str = camelot or key or ""

    parts = [path.stem[:3] if path.stem[:2].isdigit() else "00", safe_title]
    if bpm_str:
        parts.append(bpm_str)
    if key_str:
        parts.append(key_str)

    new_name = "_".join(parts) + ".wav"
    new_path = path.with_name(new_name)

    if new_path != path:
        path.rename(new_path)
        path = new_path

    # Write rich sidecar (already useful for our own tools + some DJ apps read JSON sidecars)
    meta = {
        "title": title or safe_title,
        "artist": artist,
        "bpm": round(bpm, 1) if bpm else None,
        "key": key,
        "camelot": camelot,
        "comment": comment or SAFETY_NOTE,
        "tagged_by": "forage-dj",
        "tagged_at": datetime.now(timezone.utc).isoformat(),
    }
    sidecar = path.with_suffix(".wav.json")
    sidecar.write_text(json.dumps(meta, indent=2))

    logger.info("Tagged for DJ apps: %s (BPM=%s Key=%s)", path.name, bpm_str, key_str)
    return path
