"""Shared utilities: config, logging bootstrap, metadata embedding, paths.

All generated content must carry the harm-reduction safety note.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
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
        "generated_at": datetime.utcnow().isoformat() + "Z",
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
