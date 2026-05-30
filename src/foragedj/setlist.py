"""Setlist generation & library organization.

This module powers the "generate full setlist, walk away, come back to a ready-to-jam library"
feature the user requested.

- Loads a manifest (YAML/JSON) with locked seed
- Generates every track using that seed (via audio_gen)
- Runs BPM + key analysis (reuses existing analysis.py)
- Organizes everything into libraries/<set-name>-seedXXXX/
- Produces a rich library.json with harmonic mixing suggestions (Camelot wheel)
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from . import analysis
from .audio_gen import generate_track
from .utils import SAFETY_NOTE

logger = logging.getLogger(__name__)

@dataclass
class TrackResult:
    id: str
    prompt: str
    duration: float
    model: str
    seed: int
    file: str
    bpm: float
    key: str
    camelot: str
    generated_at: str

@dataclass
class SetlistLibrary:
    name: str
    seed: int
    manifest_path: str
    library_dir: str
    generated_at: str
    tracks: List[TrackResult]
    harmonic_suggestions: Dict[str, List[str]]   # track_id -> list of compatible track_ids
    energy_estimates: Dict[str, float]           # rough 0-1 energy per track for arc planning
    recommended_transitions: Dict[str, List[Dict[str, Any]]]  # from_id -> top suggested next tracks + reasons

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "seed": self.seed,
            "manifest_path": self.manifest_path,
            "library_dir": self.library_dir,
            "generated_at": self.generated_at,
            "total_tracks": len(self.tracks),
            "safety_note": SAFETY_NOTE,
            "tracks": [asdict(t) for t in self.tracks],
            "harmonic_suggestions": self.harmonic_suggestions,
            "energy_estimates": self.energy_estimates,
            "recommended_transitions": self.recommended_transitions,
        }


def _safe_folder_name(name: str, seed: int) -> str:
    """Produce clean, readable folder names like 'Bassline_Dominion_House_Ignition_Seed424242'."""
    # Strip seed parentheticals and variants so we don't duplicate
    clean = re.sub(r'\s*\(Seed\s*\d+\)', '', name, flags=re.IGNORECASE)
    clean = re.sub(r'\s*[-–—]?\s*Seed\s*\d+', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'[^\w\s-]', '', clean).strip()
    slug = re.sub(r'[-\s]+', '_', clean)
    slug = re.sub(r'_+', '_', slug).strip('_')
    return f"{slug}_Seed{seed}"


def _estimate_energy(prompt: str, bpm: float) -> float:
    """Rough 0-1 energy rating from prompt keywords + BPM. Used for arc + transition advice."""
    p = (prompt or "").lower()
    e = 0.45
    build_kw = ["drop", "peak", "massive", "finale", "hands", "euphoric", "hard", "industrial", "distorted", "high energy"]
    chill_kw = ["breakdown", "uplifting", "pads", "emotional", "groovy", "funky", "late night", "chill"]
    for k in build_kw:
        if k in p:
            e += 0.12
    for k in chill_kw:
        if k in p:
            e -= 0.10
    e += (bpm - 126) / 30.0
    return max(0.2, min(0.95, round(e, 2)))


def load_manifest(path: Path) -> Dict[str, Any]:
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(path.read_text())
    else:
        return json.loads(path.read_text())


def generate_setlist(
    manifest_path: Path,
    output_root: Path = Path("libraries"),
    progress_callback: Optional[callable] = None,
    dry: bool = False,
) -> SetlistLibrary:
    """
    The main "walk away" feature: generate full locked-seed setlist, organize for DJ use, then walk away.

    Improvements for real "set it and forget it":
    - Clean folder naming (no ugly _-_ artifacts)
    - playlist.txt (simple text file loadable by most DJ software)
    - Rich harmonic + energy arc + concrete transition recommendations in library.json
    - Resume support: skips tracks whose target WAV already exists
    - ETA + clear % progress printed as it runs

    Example:
        library = generate_setlist(
            Path("setlists/bassline_dominion_seed424242.yaml"),
            output_root=Path("libraries")
        )
        # Go make coffee / sleep. Come back to ready library + playlist.txt + suggestions.
    """
    manifest = load_manifest(manifest_path)
    name = manifest["name"]
    seed = manifest["seed"]
    tracks_spec = manifest["tracks"]
    total = len(tracks_spec)

    safe_name = _safe_folder_name(name, seed)
    library_dir = output_root / safe_name
    library_dir.mkdir(parents=True, exist_ok=True)

    tracks: List[TrackResult] = []

    print(f"\n🎛️  Generating setlist: {name}")
    print(f"   Locked seed: {seed}")
    print(f"   Output: {library_dir}")
    print(f"   Tracks: {total}  |  Resume: will skip existing WAVs\n")

    overall_start = time.perf_counter()
    gen_times: List[float] = []

    for i, track in enumerate(tracks_spec, 1):
        # Normalize id to padded string "01", "02" etc (yaml ints become correct)
        raw_id = track.get("id", f"{i:02d}")
        track_id = str(raw_id).zfill(2)
        prompt = track["prompt"]
        duration = track.get("duration", 60)
        model = track.get("model", "small-music")

        final_name = f"{track_id}_{seed}.wav"
        final_path = library_dir / final_name

        # === RESUME SUPPORT (core walkaway friendliness) ===
        # Exists (even 0-byte from prior dry/touch or partial) => skip expensive generation step.
        # For real runs: delete the WAV manually if you want to force re-gen of a bad file.
        already_exists = final_path.exists()
        if already_exists:
            print(f"[{i}/{total}] {track_id}: {prompt[:55]}...  [SKIP - already on disk]")
            skip_gen = True
        else:
            print(f"[{i}/{total}] {track_id}: {prompt[:55]}...")
            skip_gen = False

        if progress_callback:
            progress_callback((i - 1) / total, f"{'skipping' if skip_gen else 'generating'} {track_id}...")

        track_start = time.perf_counter()

        if dry:
            if not skip_gen:
                # Do not create 0-byte placeholder files — they confuse DJ software
                print(f"    [dry] Would generate {final_name}")
            bpm, key, camelot = 128.0, "Am", "8A"
        else:
            if skip_gen:
                # Re-analyze existing file so library.json is accurate (cheap)
                res = analysis.detect_bpm_key(final_path)
                bpm, key, camelot = res.bpm, res.key, res.camelot
            else:
                wav_path = generate_track(
                    prompt=prompt,
                    seed=seed,           # <-- LOCKED SEED for the whole setlist (key feature)
                    duration=duration,
                    model=model,
                    progress_callback=progress_callback,
                )
                # Ensure nice name inside the library folder
                if wav_path != final_path:
                    import shutil
                    shutil.copy2(wav_path, final_path)

                # Analyze for harmonic mixing (BPM + Camelot key)
                res = analysis.detect_bpm_key(final_path)
                bpm, key, camelot = res.bpm, res.key, res.camelot

        gen_time = time.perf_counter() - track_start
        if not (dry or skip_gen):
            gen_times.append(gen_time)

        result = TrackResult(
            id=track_id,
            prompt=prompt,
            duration=duration,
            model=model,
            seed=seed,
            file=str(final_path.relative_to(library_dir)),
            bpm=bpm,
            key=key,
            camelot=camelot,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        tracks.append(result)

        # Live ETA + progress (clear feedback while you walk away)
        elapsed = time.perf_counter() - overall_start
        done = i
        avg = elapsed / done if done > 0 else 30.0
        remaining = avg * (total - done)
        eta_min = int(remaining // 60)
        eta_sec = int(remaining % 60)
        eta_str = f"{eta_min}m{eta_sec:02d}s" if remaining > 5 else "<5s"
        pct = int(done / total * 100)
        print(f"    {pct:3d}% | elapsed {int(elapsed)}s | ETA ~{eta_str} | last {gen_time:.1f}s")

    # === RICH HARMONIC + ENERGY + TRANSITION SUGGESTIONS (post all analysis) ===
    energy_estimates: Dict[str, float] = {}
    harmonic_suggestions: Dict[str, List[str]] = {}
    recommended_transitions: Dict[str, List[Dict[str, Any]]] = {}

    for tr in tracks:
        energy_estimates[tr.id] = _estimate_energy(tr.prompt, tr.bpm)

    for tr in tracks:
        # All Camelot-compatible partners (fixed: full set, not just prior)
        compat = [o.id for o in tracks
                  if o.id != tr.id and analysis.camelot_compatible(tr.camelot, o.camelot)]
        harmonic_suggestions[tr.id] = compat

        # Concrete transition recommendations with reasons (energy arc aware)
        trans: List[Dict[str, Any]] = []
        for o in tracks:
            if o.id == tr.id:
                continue
            if not analysis.camelot_compatible(tr.camelot, o.camelot):
                continue
            e1, e2 = energy_estimates[tr.id], energy_estimates[o.id]
            de = e2 - e1
            reason = f"Camelot {tr.camelot}→{o.camelot}"
            if de > 0.12:
                reason += " + energy build"
            elif de < -0.12:
                reason += " + energy drop/break"
            else:
                reason += " + energy steady"
            if abs(tr.bpm - o.bpm) >= 2:
                reason += f" (bpm {tr.bpm:.0f}→{o.bpm:.0f})"
            score = round(1.0 - abs(de) * 0.6 + (0.2 if de >= 0 else 0), 2)
            trans.append({
                "to": o.id,
                "reason": reason,
                "score": max(0.1, score),
                "bpm_delta": round(o.bpm - tr.bpm, 1),
                "energy_delta": round(de, 2),
            })
        trans.sort(key=lambda x: -x["score"])
        recommended_transitions[tr.id] = trans[:3]  # top-3 practical suggestions per track

    # Build final library object (now includes rich DJ guidance)
    library = SetlistLibrary(
        name=name,
        seed=seed,
        manifest_path=str(manifest_path),
        library_dir=str(library_dir),
        generated_at=datetime.now(timezone.utc).isoformat(),
        tracks=tracks,
        harmonic_suggestions=harmonic_suggestions,
        energy_estimates=energy_estimates,
        recommended_transitions=recommended_transitions,
    )

    # Write master library.json (machine + human readable)
    library_file = library_dir / "library.json"
    library_file.write_text(json.dumps(library.to_dict(), indent=2))

    # === playlist.txt for DJ software (Traktor, Serato, Rekordbox, Engine, etc.) ===
    playlist_path = library_dir / "playlist.txt"
    pl_lines = [
        f"# {name}",
        f"# forage-dj setlist | locked seed {seed} | {len(tracks)} tracks",
        f"# generated_at: {library.generated_at}",
        f"# manifest: {manifest_path}",
        "#",
        "# SIMPLE PLAYLIST - drag folder or this list into your DJ software.",
        "# Files are numbered in the intended performance / energy arc order.",
        "# See library.json for full BPM, Camelot keys, energy estimates, and transition ideas.",
        "#",
    ]
    for t in tracks:
        short = (t.prompt or "")[:48].replace("\n", " ").strip()
        pl_lines.append(f"{t.file}\t# {t.id} | {t.bpm:.0f}bpm {t.key}/{t.camelot} | {short}")
    pl_lines.append("")
    pl_lines.append("# === Top transition recommendations (from library.json) ===")
    for tid, recs in list(recommended_transitions.items())[:4]:
        for r in recs[:1]:
            pl_lines.append(f"# {tid} → {r['to']}: {r['reason']}")
    pl_lines.append("")
    pl_lines.append("# Safety: " + SAFETY_NOTE)
    playlist_path.write_text("\n".join(pl_lines) + "\n")

    total_elapsed = time.perf_counter() - overall_start
    print(f"\n✅ Setlist complete!  ({total_elapsed:.1f}s total)")
    print(f"   Library: {library_dir}")
    print(f"   Tracks:  {len(tracks)}")
    print(f"   Wrote:   library.json + playlist.txt")
    print(f"   Ready for harmonic mixing — open library.json for energy arc + transition recs.")
    if gen_times:
        print(f"   Avg gen time per track: {sum(gen_times)/len(gen_times):.1f}s")

    return library
