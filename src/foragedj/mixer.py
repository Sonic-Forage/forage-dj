"""Real-time 2-deck mixer engine.

Uses sounddevice + pedalboard + numpy for low-latency playback
(we intentionally dropped python-rtmixer for packaging reliability).

See docs/ARCHITECTURE.md:26, AGENTIC_BUILD_PLAN Phase 1 task 2,
and swarm agent 019e7a00-4c1a-7ba0-bb9a-860ec237b7c4 output (archived in .grok/).

Target: <10-15 ms audible latency on controls. Potato-machine friendly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

HAS_AUDIO = False

# Lazy imports — sounddevice loads PortAudio at import time, which may not exist in minimal envs
_sd = None
_pedalboard_classes = None

def _ensure_audio_libs():
    global HAS_AUDIO, _sd, _pedalboard_classes
    if HAS_AUDIO:
        return True
    try:
        import sounddevice as sd
        from pedalboard import (Pedalboard, Gain, LowShelfFilter, PeakFilter,
                                HighShelfFilter, LowpassFilter, HighpassFilter, Limiter)
        _sd = sd
        _pedalboard_classes = (Pedalboard, Gain, LowShelfFilter, PeakFilter,
                               HighShelfFilter, LowpassFilter, HighpassFilter, Limiter)
        HAS_AUDIO = True
        return True
    except Exception:
        HAS_AUDIO = False
        return False

logger = logging.getLogger(__name__)


@dataclass
class Deck:
    """Single playback deck state + controls."""
    id: int
    path: Optional[Path] = None
    loaded: bool = False
    playing: bool = False
    position: float = 0.0          # seconds
    volume: float = 0.8
    eq_low: float = 0.0            # dB
    eq_mid: float = 0.0
    eq_high: float = 0.0
    filter_cutoff: float = 20000.0  # Hz (low-pass)
    filter_type: str = "lowpass"    # or "highpass"
    pitch: float = 1.0              # playback rate
    bpm: float = 128.0
    key: str = "Am"

    # Internal
    _audio: Optional[np.ndarray] = field(default=None, repr=False)
    _sr: int = 44100


@dataclass
class Mixer:
    """Singleton real-time mixer. Two-deck + master for MVP."""
    deck1: Deck = field(default_factory=lambda: Deck(1))
    deck2: Deck = field(default_factory=lambda: Deck(2))
    crossfader: float = 0.0          # -1.0 (full left) ... +1.0 (full right)
    master_volume: float = 0.9
    limiter: bool = True

    _stream = None  # sounddevice / rtmixer handle

    def load_deck(self, deck_id: int, path: Path) -> None:
        """Load a WAV into a deck (analysis happens upstream)."""
        from . import analysis  # local import to avoid circulars at import time

        d = self.deck1 if deck_id == 1 else self.deck2
        d.path = Path(path)
        # TODO (Phase 1): actually load audio buffer + resample if needed
        # For now just mark loaded and pull BPM/key from analysis
        try:
            res = analysis.detect_bpm_key(d.path)
            d.bpm = res.bpm
            d.key = res.key
            d.loaded = True
            logger.info("Loaded %s into deck %s (%.1f BPM, %s)", path.name, deck_id, d.bpm, d.key)
        except Exception as e:
            logger.warning("Analysis failed on load: %s", e)
            d.loaded = True  # still playable as raw file later

    def play(self, deck_id: int) -> None:
        d = self.deck1 if deck_id == 1 else self.deck2
        if not d.loaded:
            raise RuntimeError(f"Deck {deck_id} has no track loaded")
        d.playing = True
        logger.debug("Deck %s play", deck_id)

    def pause(self, deck_id: int) -> None:
        d = self.deck1 if deck_id == 1 else self.deck2
        d.playing = False
        logger.debug("Deck %s pause", deck_id)

    def set_crossfader(self, value: float) -> None:
        self.crossfader = max(-1.0, min(1.0, value))

    # === Real-time engine contributed by swarm agent (Mixer + GUI) ===
    # Full architecture + callback skeleton from .grok/swarm-outputs/mixer-gui-agent-...

    _sr: int = 44100
    _stream = None
    _deck_boards: dict = field(default_factory=dict, repr=False)

    def _get_or_build_board(self, d: Deck) -> "Pedalboard":
        if not HAS_AUDIO:
            return None
        board = self._deck_boards.get(d.id)
        if board is None:
            board = Pedalboard([
                Gain(gain_db=d.volume * 0),  # placeholder
                LowShelfFilter(cutoff_frequency_hz=250, gain_db=d.eq_low),
                PeakFilter(cutoff_frequency_hz=1000, gain_db=d.eq_mid, q=1.0),
                HighShelfFilter(cutoff_frequency_hz=4000, gain_db=d.eq_high),
                LowpassFilter(cutoff_frequency_hz=d.filter_cutoff) if d.filter_type == "lowpass"
                else HighpassFilter(cutoff_frequency_hz=d.filter_cutoff),
            ])
            self._deck_boards[d.id] = board
        # Mutate live (very cheap)
        board[0].gain_db = 20 * (d.volume - 0.8)   # rough mapping
        board[1].gain_db = d.eq_low
        board[2].gain_db = d.eq_mid
        board[3].gain_db = d.eq_high
        filt = board[4]
        filt.cutoff_frequency_hz = d.filter_cutoff
        return board

    def load_deck(self, deck_id: int, path: Path) -> None:
        """Load a WAV into a deck + actual audio buffer for playback."""
        from . import analysis

        d = self.deck1 if deck_id == 1 else self.deck2
        d.path = Path(path)

        try:
            import librosa
            audio, sr = librosa.load(str(path), sr=self._sr, mono=False)
            if audio.ndim == 1:
                audio = np.stack([audio, audio], axis=1)
            d._audio = audio.T.astype(np.float32)  # shape (n_samples, 2)
            d._sr = sr

            res = analysis.detect_bpm_key(d.path)
            d.bpm = res.bpm
            d.key = res.key
            d.loaded = True
            logger.info("Loaded %s into deck %s (%.1f BPM, %s, %d samples)",
                        path.name, deck_id, d.bpm, d.key, len(d._audio))
        except Exception as e:
            logger.warning("Audio load failed: %s", e)
            d.loaded = True

    def start(self) -> None:
        if not HAS_AUDIO:
            logger.warning("sounddevice/pedalboard not available — mixer running in stub mode")
            return
        if self._stream is not None:
            return
        self._stream = sd.OutputStream(
            samplerate=self._sr,
            channels=2,
            dtype="float32",
            blocksize=256,
            latency="low",
            callback=self._audio_callback,
        )
        self._stream.start()
        logger.info("Mixer real-time stream started (blocksize=256, latency=low)")

    def stop(self) -> None:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            logger.info("Mixer stream stopped")

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            logger.debug("sounddevice status: %s", status)
        out = np.zeros((frames, 2), dtype=np.float32)
        cf = self.crossfader
        theta = (cf + 1) * np.pi / 4
        g1, g2 = np.cos(theta), np.sin(theta)
        master = self.master_volume

        for d, g in ((self.deck1, g1), (self.deck2, g2)):
            if not (d.playing and d.loaded and d._audio is not None):
                continue
            idx = np.arange(frames) * d.pitch + d.position
            n = len(d._audio)
            chunk = np.zeros((frames, 2), dtype=np.float32)
            for ch in range(2):
                chunk[:, ch] = np.interp(idx, np.arange(n), d._audio[:, ch],
                                         left=0.0, right=0.0)
            board = self._get_or_build_board(d)
            if board is not None:
                chunk = board.process(chunk, sample_rate=d._sr)
            out += chunk * (d.volume * g)

        if self.limiter and HAS_AUDIO:
            out = Limiter().process(out * master, sample_rate=self._sr)
        else:
            out *= master

        outdata[:] = np.clip(out, -1.0, 1.0)

        # Advance positions (basic looping for MVP)
        for d in (self.deck1, self.deck2):
            if d.playing and d._audio is not None:
                d.position += frames * d.pitch
                if d.position >= len(d._audio):
                    d.position = 0.0

    def get_state(self) -> dict:
        """Snapshot for GUI / hardware / voice."""
        return {
            "deck1": self._deck_dict(self.deck1),
            "deck2": self._deck_dict(self.deck2),
            "crossfader": round(self.crossfader, 3),
            "master_volume": self.master_volume,
        }

    @staticmethod
    def _deck_dict(d: Deck) -> dict:
        return {
            "id": d.id,
            "loaded": d.loaded,
            "playing": d.playing,
            "volume": round(d.volume, 3),
            "bpm": d.bpm,
            "key": d.key,
            "position": round(d.position, 2),
        }
