#!/usr/bin/env python3
"""
Forage Radio — Terminal Realtime Radio TUI
Plays generated ComfyUI tracks (Stable Audio + ACE-Step) as a live radio station.
"""

from __future__ import annotations

import asyncio
import glob
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import List, Optional

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Button, DataTable, Footer, Header, Label, ProgressBar, Static

# Known locations where ComfyUI drops audio files
AUDIO_DIRS = [
    Path("/mnt/z/C0MFY/ComfyUI/output/audio"),
    Path("/mnt/z/IMF2045/forage-dj/comfyui_output/audio"),
    Path("/mnt/z/IMF2045/forage-dj/generated"),
]

class ForageRadioApp(App):
    """Main Radio TUI."""

    CSS = """
    Screen { background: #0f0f0f; }
    
    #now-playing {
        background: #1a1a1a;
        border: thick #00f5ff;
        padding: 1 2;
        margin: 1;
    }
    
    #track-title {
        color: #00f5ff;
        text-style: bold;
        text-align: center;
    }
    
    #track-prompt {
        color: #888;
        text-align: center;
    }
    
    #playlist {
        height: 1fr;
    }
    
    DataTable {
        background: #111;
    }
    
    Button {
        background: #222;
    }
    
    Button:hover {
        background: #333;
    }
    
    .status {
        color: #0f0;
        text-align: center;
    }
    """

    BINDINGS = [
        ("space", "toggle_play", "Play/Pause"),
        ("n", "next_track", "Next"),
        ("p", "prev_track", "Previous"),
        ("r", "refresh", "Refresh Playlist"),
        ("q", "quit", "Quit"),
    ]

    tracks: reactive[List[dict]] = reactive([])
    current_index: reactive[int] = reactive(0)
    is_playing: reactive[bool] = reactive(False)

    def __init__(self):
        super().__init__()
        self.current_process: Optional[subprocess.Popen] = None
        self._playback_thread: Optional[threading.Thread] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="now-playing"):
            yield Label("FORAGE RADIO", id="station-name")
            yield Label("No track loaded", id="track-title")
            yield Label("", id="track-prompt")
            yield ProgressBar(id="progress", total=100)
            with Horizontal():
                yield Button("⏮ Prev", id="prev", variant="primary")
                yield Button("▶ Play", id="play", variant="success")
                yield Button("⏭ Next", id="next", variant="primary")
                yield Button("⟳ Refresh", id="refresh")

        yield DataTable(id="playlist", zebra_stripes=True)

        yield Footer()

    def on_mount(self) -> None:
        self.title = "FORAGE RADIO"
        self.sub_title = "Realtime ComfyUI Radio"

        # Setup playlist table
        table = self.query_one("#playlist", DataTable)
        table.add_columns(" # ", "Track", "Duration")
        table.focus()

        self.refresh_playlist()

        # Auto-refresh playlist every 20 seconds
        self.set_interval(20, self.refresh_playlist)

        # Start with first track if available
        if self.tracks:
            self.play_track(0)

    def refresh_playlist(self) -> None:
        """Scan known directories for new .mp3 files."""
        found: List[dict] = []

        for audio_dir in AUDIO_DIRS:
            if not audio_dir.exists():
                continue
            for mp3 in sorted(audio_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True):
                # Try to make a nice title
                name = mp3.stem.replace("_", " ").title()
                if len(name) > 50:
                    name = name[:47] + "..."

                found.append({
                    "path": str(mp3),
                    "title": name,
                    "filename": mp3.name,
                })

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for t in found:
            if t["path"] not in seen:
                seen.add(t["path"])
                unique.append(t)

        self.tracks = unique[:50]  # limit

        # Update table
        table = self.query_one("#playlist", DataTable)
        table.clear()
        for i, track in enumerate(self.tracks):
            table.add_row(
                f"{i+1:02d}",
                track["title"],
                "—",
                key=track["path"]
            )

        # Highlight current
        if self.tracks and 0 <= self.current_index < len(self.tracks):
            try:
                table.cursor_coordinate = (self.current_index, 0)
            except Exception:
                pass

    def play_track(self, index: int) -> None:
        """Play a specific track by index."""
        if not self.tracks or index < 0 or index >= len(self.tracks):
            return

        self.current_index = index
        track = self.tracks[index]

        # Stop any current playback
        self.stop_playback()

        # Update UI
        title_widget = self.query_one("#track-title", Label)
        title_widget.update(track["title"])

        prompt_widget = self.query_one("#track-prompt", Label)
        prompt_widget.update(f"Playing from ComfyUI → {track['filename']}")

        # Start playback using ffplay (headless, reliable)
        try:
            self.current_process = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", track["path"]],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.is_playing = True

            # Watch for process end to auto-advance
            threading.Thread(target=self._watch_process, daemon=True).start()

        except FileNotFoundError:
            self.notify("ffplay not found. Install ffmpeg.", severity="error")
        except Exception as e:
            self.notify(f"Playback error: {e}", severity="error")

        # Update table highlight
        table = self.query_one("#playlist", DataTable)
        try:
            table.cursor_coordinate = (index, 0)
        except Exception:
            pass

    def _watch_process(self) -> None:
        """Background thread: auto-advance when track finishes."""
        if self.current_process:
            self.current_process.wait()
            if self.is_playing:  # only advance if we didn't manually stop
                self.call_from_thread(self.next_track)

    def stop_playback(self) -> None:
        """Stop current playback."""
        self.is_playing = False
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except Exception:
                pass
            self.current_process = None

    def next_track(self) -> None:
        if not self.tracks:
            return
        next_idx = (self.current_index + 1) % len(self.tracks)
        self.play_track(next_idx)

    def prev_track(self) -> None:
        if not self.tracks:
            return
        prev_idx = (self.current_index - 1) % len(self.tracks)
        self.play_track(prev_idx)

    # === Button handlers ===
    @on(Button.Pressed, "#play")
    def action_toggle_play(self) -> None:
        if self.is_playing:
            self.stop_playback()
            self.query_one("#play", Button).label = "▶ Play"
        else:
            if self.tracks:
                self.play_track(self.current_index)
                self.query_one("#play", Button).label = "⏸ Pause"

    @on(Button.Pressed, "#next")
    def action_next_track(self) -> None:
        self.next_track()

    @on(Button.Pressed, "#prev")
    def action_prev_track(self) -> None:
        self.prev_track()

    @on(Button.Pressed, "#refresh")
    def action_refresh(self) -> None:
        self.refresh_playlist()
        self.notify("Playlist refreshed")

    # Keyboard actions
    def action_toggle_play(self) -> None:
        self.action_toggle_play()

    def action_next_track(self) -> None:
        self.next_track()

    def action_prev_track(self) -> None:
        self.prev_track()

    def action_refresh(self) -> None:
        self.refresh_playlist()

    def on_unmount(self) -> None:
        self.stop_playback()


if __name__ == "__main__":
    app = ForageRadioApp()
    app.run()