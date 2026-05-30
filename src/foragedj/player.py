"""Sonic Forage Media Player — Region & Arrangement Playback Engine

This is the beginning of turning the existing mixer + workstation into a real
media player / performance tool.

Current focus (Phase A):
- Play individual regions from a Workstation Session
- Basic transport (play, pause, stop, seek)
- Play full arrangements in order
- Integration point for future hotcues, stems, recording, etc.

All paths respect the strict Z: drive containment.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import numpy as np

from . import paths
from .mixer import Mixer, HAS_AUDIO
from .workstation import Session, Track, Region

logger = logging.getLogger(__name__)


@dataclass
class PlaybackState:
    """Current playback state for the media player."""
    is_playing: bool = False
    current_track_id: Optional[str] = None
    current_region_id: Optional[str] = None
    position: float = 0.0          # seconds within current region
    loop_enabled: bool = False
    session: Optional[Session] = None


class MediaPlayer:
    """
    High-level media player built on top of the existing Mixer.

    Designed to feel like a proper DAW transport while staying lightweight
    enough for potato machines and live performance.
    """

    def __init__(self):
        self.mixer = Mixer()
        self.state = PlaybackState()
        self._lock = threading.Lock()
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def load_session(self, session: Session) -> None:
        """Load a full workstation session for playback."""
        with self._lock:
            self.state.session = session
            self.state.current_track_id = None
            self.state.current_region_id = None
            self.state.position = 0.0
            logger.info("Loaded session '%s' into media player (%d tracks)",
                        session.name, len(session.tracks))

    def play_region(self, track_id: str, region_id: str, loop: bool = False) -> None:
        """Play a specific region from the loaded session."""
        if not self.state.session:
            raise RuntimeError("No session loaded. Call load_session() first.")

        track = next((t for t in self.state.session.tracks if t.id == track_id), None)
        if not track:
            raise ValueError(f"Track {track_id} not found in session")

        region = next((r for r in track.regions if r.id == region_id), None)
        if not region:
            raise ValueError(f"Region {region_id} not found in track {track_id}")

        with self._lock:
            self.state.current_track_id = track_id
            self.state.current_region_id = region_id
            self.state.position = 0.0
            self.state.loop_enabled = loop

        # Load the audio for this region into a mixer deck
        # For now we load the full source and will slice in the callback
        # (future optimization: pre-slice regions for lower memory)
        self.mixer.load_deck(1, region.source_file or track.source_path)

        self._start_playback(region)

    def _start_playback(self, region: Region) -> None:
        """Internal playback loop for a region."""
        self._stop_event.clear()

        def playback_worker():
            region_duration = region.end - region.start
            start_time = time.time()

            self.mixer.play(1)

            while not self._stop_event.is_set():
                elapsed = time.time() - start_time
                position = elapsed % region_duration if self.state.loop_enabled else elapsed

                with self._lock:
                    self.state.position = position
                    self.state.is_playing = True

                if not self.state.loop_enabled and position >= region_duration:
                    break

                time.sleep(0.05)  # ~20 fps state updates

            self.mixer.pause(1)
            with self._lock:
                self.state.is_playing = False

        self._playback_thread = threading.Thread(target=playback_worker, daemon=True)
        self._playback_thread.start()

    def stop(self) -> None:
        """Stop current playback."""
        self._stop_event.set()
        self.mixer.pause(1)
        with self._lock:
            self.state.is_playing = False
            self.state.position = 0.0

    def get_state(self) -> PlaybackState:
        """Thread-safe snapshot of current playback state."""
        with self._lock:
            return PlaybackState(
                is_playing=self.state.is_playing,
                current_track_id=self.state.current_track_id,
                current_region_id=self.state.current_region_id,
                position=self.state.position,
                loop_enabled=self.state.loop_enabled,
                session=self.state.session,
            )

    # --- Future expansion points (stubs for now) ---

    def set_hotcue(self, name: str, position: float) -> None:
        """Set a hotcue at the given position (seconds)."""
        logger.info("Hotcue '%s' set at %.2fs (not yet persisted)", name, position)

    def jump_to_hotcue(self, name: str) -> None:
        """Jump playback to a previously set hotcue."""
        logger.info("Jump to hotcue '%s' requested (not yet implemented)", name)

    def enable_stem(self, stem_name: str, enabled: bool = True) -> None:
        """Mute/unmute a specific stem during playback (requires pre-split stems)."""
        logger.info("Stem control for '%s' = %s (not yet implemented)", stem_name, enabled)


# Global singleton for easy CLI / OS access
media_player = MediaPlayer()
