#!/usr/bin/env python3
"""
Sonic Forage Swarm Distribution App

Autonomous pipeline:
- Create / pull generative material (sessions, libraries, live recordings)
- Organize + analyze (BPM, key, energy, harmonic suggestions)
- Compile into DJ-ready packages (uses existing tag-library logic)
- Distribute (export ready packages + basic API stubs)
- Seed Bomb (autonomously release generative seeds back into the world)

Run from project root (everything stays on the mounted drive):
    uv run python scripts/swarm_distributor.py --input sessions/MySession --mode full --seed-bomb

See skills/swarm-distribution/SKILL.md for the full vision.
"""

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from foragedj import paths, analysis, workstation

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
OUTPUT_DIR = PROJECT_ROOT / "generated" / "swarm-distribution"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEED_BOMB_DIR = PROJECT_ROOT / "public" / "seeds"
SEED_BOMB_DIR.mkdir(parents=True, exist_ok=True)


def load_session_or_library(input_path: Path) -> Dict[str, Any]:
    """Load a workstation session or a library folder."""
    if (input_path / "session.json").exists():
        sess = workstation.Session.load(input_path)
        return {
            "type": "session",
            "name": sess.name,
            "tracks": [
                {
                    "file": str(t.source_path),
                    "bpm": t.bpm,
                    "key": t.key,
                    "regions": [
                        {"prompt": r.prompt, "seed": r.seed, "start": r.start, "end": r.end}
                        for r in t.regions
                    ]
                }
                for t in sess.tracks
            ]
        }
    elif (input_path / "library.json").exists():
        data = json.loads((input_path / "library.json").read_text())
        return {"type": "library", "name": data.get("name", input_path.name), **data}
    else:
        raise ValueError(f"No session.json or library.json found in {input_path}")


def analyze_material(material: Dict[str, Any]) -> Dict[str, Any]:
    """Run deep analysis (reuses existing analysis + adds swarm-level insights)."""
    analyzed_tracks = []
    for track in material.get("tracks", []):
        try:
            res = analysis.detect_bpm_key(track["file"])
            track["bpm"] = res.bpm
            track["key"] = res.key
            track["camelot"] = res.camelot
            track["energy_estimate"] = "high" if res.bpm > 125 else "medium"
        except Exception:
            pass
        analyzed_tracks.append(track)

    material["tracks"] = analyzed_tracks
    material["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    material["swarm_notes"] = "Autonomously analyzed by Swarm Distribution App"
    return material


def compile_package(material: Dict[str, Any], output_name: str) -> Path:
    """Compile into a clean, DJ-ready distribution package."""
    pkg_dir = OUTPUT_DIR / output_name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Copy tracks (in real version this would also re-encode/normalize if needed)
    for track in material.get("tracks", []):
        src = Path(track["file"])
        if src.exists():
            dst = pkg_dir / src.name
            shutil.copy2(src, dst)

    # Write rich package metadata
    package_meta = {
        "name": material.get("name", output_name),
        "generated_by": "Sonic Forage Swarm Distribution App",
        "created": datetime.now(timezone.utc).isoformat(),
        "tracks": material.get("tracks", []),
        "swarm_metadata": material.get("swarm_notes", "")
    }
    (pkg_dir / "package.json").write_text(json.dumps(package_meta, indent=2))

    # Also produce a clean playlist
    playlist = [t["file"] for t in material.get("tracks", []) if "file" in t]
    (pkg_dir / "playlist.m3u").write_text("\n".join(playlist))

    print(f"✅ Compiled distribution package: {pkg_dir}")
    return pkg_dir


def distribute(package_dir: Path, mode: str = "local"):
    """Stub for autonomous distribution."""
    print(f"📦 Preparing distribution for mode: {mode}")

    if mode == "local":
        print("   → Local export ready. You can upload manually or via your own site.")
    elif mode == "bandcamp":
        print("   → Bandcamp stub: Would need API key + manual artist approval first time.")
        print("   Package is ready at:", package_dir)
    elif mode == "ipfs":
        print("   → IPFS/Arweave stub: In real version would run `ipfs add -r` or similar.")
        print("   Package is ready at:", package_dir)
    else:
        print("   → Unknown mode. Package is ready at:", package_dir)

    print("   (Full autonomous API distribution is limited by platform approval flows.)")


def seed_bomb(material: Dict[str, Any], package_name: str):
    """Autonomous 'seed bombing' — release generative seeds back into the world."""
    seed_packet = {
        "type": "generative_seed",
        "name": package_name,
        "released": datetime.now(timezone.utc).isoformat(),
        "prompts": [t.get("prompt", "") for t in material.get("tracks", [])],
        "manifest": material,
        "license": "Creative Commons — feel free to grow your own forest",
        "philosophy": "Release seeds. Let the culture spread. Some will come back."
    }

    seed_file = SEED_BOMB_DIR / f"{package_name}_seed.json"
    seed_file.write_text(json.dumps(seed_packet, indent=2))

    print(f"🌱 SEED BOMBED: {seed_file}")
    print("   This generative seed is now released into the world.")
    print("   People can take it, remix it, and grow their own music.")


def main():
    parser = argparse.ArgumentParser(description="Sonic Forage Swarm Distribution App")
    parser.add_argument("--input", required=True, help="Path to session or library folder")
    parser.add_argument("--mode", choices=["full", "analyze", "compile", "distribute", "seed-bomb"], default="full")
    parser.add_argument("--distribute-mode", default="local", help="local | bandcamp | ipfs")
    parser.add_argument("--seed-bomb", action="store_true", help="Also release seeds publicly")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    material = load_session_or_library(input_path)
    print(f"Loaded {material['type']}: {material.get('name')}")

    if args.mode in ("full", "analyze"):
        material = analyze_material(material)

    if args.mode in ("full", "compile"):
        pkg = compile_package(material, input_path.name + "_swarm_package")

    if args.mode in ("full", "distribute"):
        pkg = OUTPUT_DIR / (input_path.name + "_swarm_package")
        distribute(pkg, args.distribute_mode)

    if args.seed_bomb or args.mode == "seed-bomb":
        seed_bomb(material, input_path.name)

    print("\n✅ Swarm Distribution run complete. All output inside the project root.")


if __name__ == "__main__":
    main()
