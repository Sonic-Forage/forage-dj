#!/usr/bin/env python3
"""
forage-dj Universal Cross-Platform Installer (Linux + Windows)

This is the recommended easy installer for both operating systems.

Usage:
    python scripts/install.py
    python scripts/install.py --full
    python -m scripts.install   # after uv sync once

It will:
- Bootstrap uv (Astral) if missing
- Create .venv
- Install dependencies (with sensible extras)
- Detect or ask for a large storage root (Z: on Linux, D:/E: on Windows, etc.)
- Generate cross-platform HF cache helpers (.env + .ps1)
- Write .grok/paths.json so all Python code finds your data
- Run `foragedj doctor --heal`
- Print OS-specific next steps (espeak-ng, audio drivers, etc.)

Run this from the forage-dj root directory.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
GROK_DIR = PROJECT_ROOT / ".grok"


def print_banner():
    print("🎧 forage-dj Universal Installer")
    print("   Cross-platform (Linux + Windows) — Sonic Forage Music Diffusion OS")
    print(f"   Python: {sys.version.split()[0]}  |  Platform: {platform.system()}")
    print()


def ensure_uv() -> bool:
    """Make sure uv is in PATH. Downloads it if necessary (works on Linux + Windows)."""
    if shutil.which("uv"):
        print(f"→ uv found: {shutil.which('uv')}")
        return True

    print("→ uv not found — bootstrapping Astral uv (cross-platform)...")
    system = platform.system()

    try:
        if system == "Windows":
            # PowerShell one-liner from Astral
            cmd = [
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                "irm https://astral.sh/uv/install.ps1 | iex"
            ]
            subprocess.check_call(cmd, shell=False)
        else:
            # curl | sh works on Linux/mac
            subprocess.check_call(
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
                shell=True
            )
        # Refresh PATH in this process
        home = Path.home()
        for candidate in [home / ".local" / "bin", home / ".cargo" / "bin"]:
            if candidate.exists():
                os.environ["PATH"] = str(candidate) + os.pathsep + os.environ.get("PATH", "")
        return shutil.which("uv") is not None
    except Exception as e:
        print(f"   Failed to auto-install uv: {e}")
        print("   Please install manually: https://docs.astral.sh/uv/getting-started/installation/")
        return False


def choose_data_root() -> Path:
    """Smart + interactive choice of large storage root (self-contained detection)."""
    # Minimal inline version of the detection logic so this runs before any sync
    system = platform.system()
    detected = None

    if system == "Linux":
        candidates = [
            Path("/mnt/z"), Path("/mnt/data"), Path("/mnt/fast"),
            Path("/data"), Path.home() / "forage-data",
            Path.home() / "Music" / "forage-dj-data",
        ]
        for p in candidates:
            if p.exists() and p.is_dir():
                detected = p
                break
    elif system == "Windows":
        for letter in ["D", "E", "F", "G", "H"]:
            p = Path(f"{letter}:/")
            if p.exists():
                detected = p / "forage-dj-data"
                break
    if not detected:
        detected = PROJECT_ROOT / "data" if system != "Windows" else (Path(os.environ.get("USERPROFILE", Path.home())) / "forage-dj-data")

    default = detected or (PROJECT_ROOT / "data")
    system = platform.system()

    print("\nLarge storage root (for checkpoints, HF cache, generated libraries):")
    if detected:
        print(f"   Auto-detected good candidate: {detected}")
    else:
        print("   No obvious large drive found — will use project-local fallback or your choice.")

    default = detected or (PROJECT_ROOT / "data")

    try:
        answer = input(f"\nUse this location? [{default}] (Y/n or enter custom path): ").strip()
    except (EOFError, KeyboardInterrupt):
        answer = ""

    if not answer or answer.lower().startswith("y"):
        return default

    if answer.lower() == "n":
        custom = input("Enter full path for large data root: ").strip()
        return Path(custom).expanduser().resolve()

    # User typed a path directly
    return Path(answer).expanduser().resolve()


def write_cross_platform_env_helpers(data_root: Path, hf_home: Path) -> None:
    GROK_DIR.mkdir(parents=True, exist_ok=True)

    # Bash / zsh / fish friendly
    env_sh = GROK_DIR / "hf-cache.env"
    env_sh.write_text(f"""# forage-dj HF cache + data root (Linux / macOS / WSL)
# Usage: source .grok/hf-cache.env

export FORAGE_DJ_DATA_ROOT="{data_root}"
export HF_HOME="{hf_home}"
export HUGGINGFACE_HUB_CACHE="$HF_HOME/hub"

echo "✅ forage-dj data root: $FORAGE_DJ_DATA_ROOT"
echo "✅ HF cache: $HF_HOME"
""")

    # PowerShell (Windows)
    env_ps1 = GROK_DIR / "hf-cache.ps1"
    env_ps1.write_text(f"""# forage-dj HF cache + data root (Windows PowerShell)
# Usage: . .grok\\hf-cache.ps1

$env:FORAGE_DJ_DATA_ROOT = "{data_root}"
$env:HF_HOME = "{hf_home}"
$env:HUGGINGFACE_HUB_CACHE = "$env:HF_HOME\\hub"

Write-Host "✅ forage-dj data root: $env:FORAGE_DJ_DATA_ROOT" -ForegroundColor Green
Write-Host "✅ HF cache: $env:HF_HOME" -ForegroundColor Green
""")

    # Also write paths.json so Python code picks it up immediately
    paths_json = GROK_DIR / "paths.json"
    paths_json.write_text(
        f'{{"data_root": "{data_root}", "hf_home": "{hf_home}"}}\n'
    )

    print(f"\n✅ Wrote cross-platform helpers:")
    print(f"   .grok/hf-cache.env   (Linux/mac/WSL)")
    print(f"   .grok/hf-cache.ps1   (Windows PowerShell)")
    print(f"   .grok/paths.json     (used automatically by Python code)")


def run_uv_sync(mode: str) -> None:
    print("\n→ Running uv sync (this may take a minute)...")
    if mode == "full":
        cmd = ["uv", "sync", "--extra", "full", "--group", "dev"]
    else:
        cmd = ["uv", "sync", "--extra", "gui", "--group", "dev"]

    subprocess.check_call(cmd, cwd=PROJECT_ROOT)


def run_doctor() -> None:
    print("\n→ Running doctor --heal...")
    subprocess.check_call(
        [sys.executable, "-m", "foragedj.cli", "doctor", "--heal"],
        cwd=PROJECT_ROOT
    )


def print_next_steps(system: str, data_root: Path) -> None:
    print("\n" + "=" * 60)
    print("✅ forage-dj installation complete (cross-platform)!")
    print("=" * 60)

    print(f"\nYour large data root is set to: {data_root}")
    print("\nActivate the environment in future terminals with:")

    if system == "Windows":
        print("   . .grok\\hf-cache.ps1          # (PowerShell - recommended)")
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .grok/hf-cache.env")
        print("   source .venv/bin/activate")

    print("\nImportant one-time / platform-specific steps:")

    if system == "Linux":
        print("  • Audio runtime (recommended):")
        print("      sudo apt install libportaudio2 portaudio19-dev ffmpeg espeak-ng")
        print("  • For best low-latency: also install JACK or PipeWire")
    elif system == "Windows":
        print("  • Install eSpeak NG (required for Kokoro TTS):")
        print("      https://github.com/espeak-ng/espeak-ng/releases  (download the .msi)")
        print("  • For serious low-latency audio: install ASIO4ALL (optional but excellent)")
        print("  • Some wheels may need Microsoft Visual C++ Redistributable (usually already present)")
    else:
        print("  • Install espeak-ng / portaudio via your package manager")

    print("\nNext commands to try:")
    print("  uv run foragedj doctor")
    print("  uv run foragedj download-models --help")
    print("  uv run foragedj os                 # boot the retro Music Diffusion OS")
    print("  uv run foragedj enhance --help")
    print("  uv run foragedj speak \"hello world\" --voice af_heart")

    print("\nFull documentation:")
    print("  docs/INSTALL.md (create this if you want a dedicated guide)")
    print("  README.md")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="forage-dj universal cross-platform installer")
    parser.add_argument("--full", action="store_true", help="Install all extras (voice, stems, audio-tools, etc.)")
    parser.add_argument("--no-doctor", action="store_true", help="Skip running doctor at the end")
    args = parser.parse_args()

    print_banner()

    if not ensure_uv():
        sys.exit(1)

    mode = "full" if args.full else "cpu"

    # Let the user choose / confirm the data root early
    data_root = choose_data_root()
    hf_home = data_root / ".cache" / "huggingface"

    print(f"\n→ Using data root: {data_root}")
    print(f"→ HF cache will live at: {hf_home}")

    # Write helpers before sync (so doctor can see them)
    write_cross_platform_env_helpers(data_root, hf_home)

    # Make sure the venv will exist in the project
    run_uv_sync(mode)

    # Activate the new venv for the rest of the process
    venv_python = PROJECT_ROOT / ".venv" / ("Scripts" if platform.system() == "Windows" else "bin") / "python"
    if venv_python.exists():
        sys.executable = str(venv_python)  # best effort

    if not args.no_doctor:
        try:
            run_doctor()
        except Exception as e:
            print(f"Doctor encountered an issue (non-fatal): {e}")

    print_next_steps(platform.system(), data_root)


if __name__ == "__main__":
    main()