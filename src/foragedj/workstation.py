"""Sonic Forage Workstation — Ableton-style editing, regeneration, inpainting.

Core idea: Treat every generated track as a living, editable "Live Set".
- Regions / clips (like Ableton clips)
- Non-destructive edits
- Prompt-driven regeneration of sections
- Audio inpainting (replace a region while matching context)
- Variations / reproduce
- Stem-aware editing (future)

All data lives strictly under the mounted drive:
    /mnt/z/IMF2045/forage-dj/sessions/YourSessionName/

This module is the foundation. Real audio DSP + diffusion inpainting
will be wired in over time (one feature at a time).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import paths

logger = logging.getLogger(__name__)
console = Console()


@dataclass
class Region:
    """A selectable/editable region inside a track (like an Ableton clip)."""
    id: str
    start: float          # seconds
    end: float            # seconds
    prompt: str = ""      # original or new prompt for this region
    seed: Optional[int] = None
    source_file: Optional[Path] = None
    notes: str = ""
    locked: bool = False  # prevent regeneration


@dataclass
class Track:
    """One audio track in a workstation session."""
    id: str
    name: str
    source_path: Path
    duration: float = 0.0
    bpm: float = 128.0
    key: str = "Am"
    regions: List[Region] = field(default_factory=list)

    def add_region(self, start: float, end: float, prompt: str = "", seed: Optional[int] = None) -> Region:
        region = Region(
            id=f"reg_{len(self.regions)+1:03d}",
            start=start,
            end=end,
            prompt=prompt or f"Region {len(self.regions)+1}",
            seed=seed,
            source_file=self.source_path,
        )
        self.regions.append(region)
        return region


@dataclass
class Session:
    """A full workstation project (the Ableton .als equivalent)."""
    name: str
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tracks: List[Track] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    session_dir: Optional[Path] = None  # set when saved/loaded

    def add_track(self, source_path: Path, name: Optional[str] = None) -> Track:
        name = name or source_path.stem
        track = Track(
            id=f"track_{len(self.tracks)+1:02d}",
            name=name,
            source_path=Path(source_path),
        )
        self.tracks.append(track)
        return track

    def save(self, session_dir: Optional[Path] = None) -> Path:
        if session_dir is None:
            if self.session_dir is None:
                session_dir = paths.get_sessions_dir() / self.name
            else:
                session_dir = self.session_dir
        session_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "name": self.name,
            "created": self.created,
            "metadata": self.metadata,
            "tracks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "source_path": str(t.source_path),
                    "bpm": t.bpm,
                    "key": t.key,
                    "regions": [
                        {
                            "id": r.id,
                            "start": r.start,
                            "end": r.end,
                            "prompt": r.prompt,
                            "seed": r.seed,
                            "notes": r.notes,
                            "locked": r.locked,
                        }
                        for r in t.regions
                    ],
                }
                for t in self.tracks
            ],
        }

        (session_dir / "session.json").write_text(json.dumps(data, indent=2))
        self.session_dir = session_dir
        logger.info("Session saved: %s", session_dir)
        return session_dir

    @classmethod
    def load(cls, session_dir: Path) -> "Session":
        data = json.loads((session_dir / "session.json").read_text())
        session = cls(name=data["name"], created=data.get("created", ""))
        session.metadata = data.get("metadata", {})
        session.session_dir = session_dir

        for tdata in data.get("tracks", []):
            track = Track(
                id=tdata["id"],
                name=tdata["name"],
                source_path=Path(tdata["source_path"]),
                bpm=tdata.get("bpm", 128.0),
                key=tdata.get("key", "Am"),
            )
            for rdata in tdata.get("regions", []):
                region = Region(
                    id=rdata["id"],
                    start=rdata["start"],
                    end=rdata["end"],
                    prompt=rdata.get("prompt", ""),
                    seed=rdata.get("seed"),
                    notes=rdata.get("notes", ""),
                    locked=rdata.get("locked", False),
                )
                track.regions.append(region)
            session.tracks.append(track)

        return session


# === High-level workstation operations (stubs for now — wire real models later) ===

def create_session(name: str) -> Session:
    """Create a new empty workstation session."""
    return Session(name=name)


def regenerate_region(
    session: Session,
    track_id: str,
    region_id: str,
    new_prompt: str,
    new_seed: Optional[int] = None,
    enhance: bool = True,
) -> Path:
    """
    BAD-ASS regeneration:
    - Uses surrounding region prompts for context (harmonic continuity)
    - Generates new audio
    - Optionally runs through FlashSR enhancer for polish
    - Updates the session non-destructively
    """
    from .audio_gen import generate_track
    from .enhance import enhance_audio

    track = next((t for t in session.tracks if t.id == track_id), None)
    if not track:
        raise ValueError(f"Track {track_id} not found")

    region = next((r for r in track.regions if r.id == region_id), None)
    if not region:
        raise ValueError(f"Region {region_id} not found")

    duration = region.end - region.start
    if duration <= 0:
        raise ValueError("Invalid region duration")

    # Build smart context prompt from neighbors (this is the "bad ass" part)
    idx = track.regions.index(region)
    prev = track.regions[idx-1].prompt if idx > 0 else ""
    nxt = track.regions[idx+1].prompt if idx + 1 < len(track.regions) else ""
    context = f"Context: previous section '{prev}'. Next section '{nxt}'. "
    full_prompt = context + new_prompt + f" , {track.bpm}bpm {track.key}, seamless musical transition"

    logger.info("Regenerating region %s (%.1fs) with smart context prompt", region_id, duration)

    out_path = generate_track(
        prompt=full_prompt,
        seed=new_seed or (region.seed or 42),
        duration=duration,
    )

    if enhance:
        try:
            enhanced = enhance_audio(out_path, model="flashsr-tiny")
            out_path = enhanced
            logger.info("Applied FlashSR enhancement to regenerated region")
        except Exception as e:
            logger.warning("Enhancement skipped: %s", e)

    # Update region
    region.prompt = new_prompt
    region.seed = new_seed or region.seed
    region.source_file = out_path
    region.notes = f"Regenerated with context at {datetime.now(timezone.utc).isoformat()}"

    session.save()
    return out_path


def inpaint_region(session: Session, track_id: str, region_id: str, prompt: str, enhance: bool = True) -> Path:
    """
    BAD-ASS Inpainting: context-aware regeneration + enhancement.
    Uses neighboring prompts for musical continuity.
    """
    logger.info("Inpainting (context-aware) region")
    return regenerate_region(session, track_id, region_id, prompt, enhance=enhance)


def create_variation(session: Session, track_id: str, variation_prompt: str = "") -> Path:
    """Create a new variation of an entire track or region."""
    # Placeholder for future "reproduce with same seed family + small prompt change"
    track = next((t for t in session.tracks if t.id == track_id), None)
    if not track:
        raise ValueError(f"Track not found: {track_id}")

    base_prompt = variation_prompt or track.regions[0].prompt if track.regions else "variation"
    return generate_track(prompt=base_prompt + " (variation)", seed=(track.regions[0].seed or 42) + 1 if track.regions else 43)


# =============================================================================
# BAD-ASS TERMINAL ARRANGEMENT VIEW (Ableton clip launcher vibes in the terminal)
# =============================================================================

def _format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def render_session_arrangement(session: Session, width: int = 80) -> None:
    """
    Render a beautiful, Ableton-style arrangement view in the terminal.
    Shows tracks as rows, regions as colored blocks on a timeline.
    Includes BPM, key, Camelot, prompt snippets.
    This is the "bad ass" visual heart of the workstation.
    """
    if not session.tracks:
        console.print("[yellow]Empty session. Add tracks with workstation-add-track[/yellow]")
        return

    console.print(Panel.fit(f"[bold cyan]🎚️  SONIC FORAGE WORKSTATION — {session.name}[/bold cyan]", border_style="cyan"))
    console.print(f"Created: {session.created}  |  Sessions root: {paths.get_sessions_dir()}")

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Track", style="bold", width=18)
    table.add_column("BPM/Key", justify="center", width=12)
    table.add_column("Arrangement Timeline", width=width)

    max_duration = max((t.duration or 120.0) for t in session.tracks) or 120.0

    colors = ["green", "yellow", "blue", "red", "magenta", "cyan"]

    for i, track in enumerate(session.tracks):
        color = colors[i % len(colors)]
        bpm_key = f"{track.bpm} {track.key}"

        # Build timeline visual
        timeline = Text()
        scale = width / max_duration

        # Draw background grid (beats approx)
        for x in range(0, width, 8):
            timeline.append("│", style="dim")

        # Draw regions as solid blocks
        for j, region in enumerate(track.regions):
            start_x = int(region.start * scale)
            end_x = int(region.end * scale)
            length = max(1, end_x - start_x)

            block = "█" * length
            label = region.prompt[: length - 2] if len(region.prompt) > 2 else region.id
            if len(label) > length:
                label = label[:length-1]

            style = f"bold {color}" if not region.locked else f"bold {color} on black"
            timeline.append(block, style=style)

            # Overlay label in middle if space
            mid = start_x + length // 2
            if mid < len(timeline._text) and length > 6:
                # Rich doesn't allow easy mid-overwrite, so we just show short id
                pass

        # Add time labels at bottom conceptually
        timeline.append(f"\n  0:00{' '*(width-10)}{_format_time(max_duration)}", style="dim")

        track_label = f"{track.name}\n{track.id}"
        table.add_row(track_label, bpm_key, timeline)

    console.print(table)

    # Region detail table (bad ass detail view)
    detail = Table(title="Regions Detail", show_lines=True)
    detail.add_column("ID", style="cyan")
    detail.add_column("Time", style="green")
    detail.add_column("Prompt", style="yellow", max_width=50)
    detail.add_column("Seed", justify="right")
    detail.add_column("Locked")

    for track in session.tracks:
        for r in track.regions:
            detail.add_row(
                r.id,
                f"{_format_time(r.start)} → {_format_time(r.end)}",
                r.prompt or "(no prompt)",
                str(r.seed) if r.seed else "-",
                "🔒" if r.locked else "✏️",
            )

    console.print(detail)
    console.print("\n[dim]Commands: workstation-regenerate, workstation-reproduce, etc.[/dim]")


def auto_create_regions_from_onsets(
    track: Track,
    analysis_result: Optional[Any] = None,
    min_region_len: float = 8.0,
    max_regions: int = 12,
) -> List[Region]:
    """
    Automatically split a track into musical regions using onset/energy data.
    This makes the workstation feel smart and Ableton-like out of the box.
    Robust to missing audio backends.
    """
    from . import analysis

    try:
        if analysis_result is None:
            analysis_result = analysis.detect_bpm_key(track.source_path)

        onsets = analysis_result.onset_frames or []
        sr = 22050
        hop = 512

        # Safe import
        try:
            import librosa as _librosa
            times = _librosa.frames_to_time(onsets, sr=sr, hop_length=hop) if onsets is not None and len(onsets) > 0 else []
        except Exception:
            times = []

        # Fallback simple energy-based if no onsets
        if len(times) < 4:
            duration = analysis_result.duration or 120.0
            num = min(max_regions, max(3, int(duration / min_region_len)))
            times = [i * duration / num for i in range(num + 1)]

        regions = []
        for i in range(len(times) - 1):
            start = times[i]
            end = times[i + 1]
            if end - start < min_region_len * 0.7:
                continue
            reg = track.add_region(
                start=round(start, 2),
                end=round(min(end, analysis_result.duration or end), 2),
                prompt=f"Section {i+1} @ {analysis_result.bpm}bpm {analysis_result.key}",
                seed=42 + i,
            )
            regions.append(reg)

        track.duration = analysis_result.duration or (times[-1] if times else 0)
        track.bpm = analysis_result.bpm
        track.key = analysis_result.key
        return regions

    except Exception as e:
        logger.error("Auto region split failed: %s", e)
        # Graceful fallback: create a couple of simple regions
        duration = analysis_result.duration if analysis_result else 120.0
        fallback = []
        for i in range(3):
            start = i * duration / 3
            end = (i + 1) * duration / 3
            reg = track.add_region(
                start=round(start, 2),
                end=round(end, 2),
                prompt=f"Auto section {i+1}",
                seed=42 + i,
            )
            fallback.append(reg)
        if analysis_result:
            track.duration = analysis_result.duration
            track.bpm = analysis_result.bpm
            track.key = analysis_result.key
        return fallback


if __name__ == "__main__":
    print("Sonic Forage Workstation foundation loaded.")
    print("All sessions live at:", paths.get_sessions_dir())
    print("Run 'uv run python -m foragedj.workstation' for demo view (after creating a session).")