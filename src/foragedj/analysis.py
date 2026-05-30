"""Audio analysis helpers (BPM, key, onset) using librosa.

Used by mixer for beat-sync and auto-mix. Camelot wheel helpers for key matching.
Part of Phase 1 core (see FEATURES_SPEC P0).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import librosa
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    bpm: float
    key: str                  # e.g. "Am", "C#"
    camelot: str              # e.g. "8A", "3B"
    duration: float
    onset_frames: Optional[np.ndarray] = None


# Very small Camelot wheel map (expand as needed)
_KEY_TO_CAMELOT = {
    "C": "8B", "Cm": "5A",
    "C#": "3B", "C#m": "12A",
    "D": "10B", "Dm": "7A",
    "D#": "5B", "D#m": "2A",
    "E": "12B", "Em": "9A",
    "F": "7B", "Fm": "4A",
    "F#": "2B", "F#m": "11A",
    "G": "9B", "Gm": "6A",
    "G#": "4B", "G#m": "1A",
    "A": "11B", "Am": "8A",
    "A#": "6B", "A#m": "3A",
    "B": "1B", "Bm": "10A",
}


def detect_bpm_key(
    path: Path | str,
    sr: int = 22050,
) -> AnalysisResult:
    """Fast BPM + musical key estimate for a WAV file.

    Returns AnalysisResult with camelot notation for easy harmonic mixing.
    """
    path = Path(path)
    y, _ = librosa.load(path, sr=sr, mono=True)

    # Tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(tempo)

    # Chroma + key estimate (simple but effective)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_avg = chroma.mean(axis=1)
    key_idx = int(chroma_avg.argmax())
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    root = keys[key_idx]

    # Crude major/minor via relative minor energy (good enough for MVP)
    # A better version would use a key template correlation.
    minor_energy = chroma_avg[(key_idx + 9) % 12]  # relative minor
    is_minor = minor_energy > (chroma_avg[key_idx] * 0.6)
    key = f"{root}m" if is_minor else root

    camelot = _KEY_TO_CAMELOT.get(key, "8A")  # safe default

    duration = librosa.get_duration(y=y, sr=sr)

    # Onsets for later beat grid / sync work
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)

    return AnalysisResult(
        bpm=round(bpm, 1),
        key=key,
        camelot=camelot,
        duration=round(duration, 2),
        onset_frames=onsets,
    )


def camelot_compatible(a: str, b: str) -> bool:
    """Return True if two Camelot keys are harmonically compatible (same or +/-1)."""
    if not a or not b:
        return False
    try:
        num_a = int(a[:-1])
        num_b = int(b[:-1])
        diff = abs(num_a - num_b)
        return diff <= 1 or diff == 11  # wrap around the wheel
    except Exception:
        return False
