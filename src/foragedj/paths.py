"""Cross-platform path resolution for forage-dj.

Handles:
- Large storage root (Z: drive on Linux, D:/E: on Windows, or user choice)
- HF cache location
- Generated libraries / checkpoints location (can be relocated)

Priority (highest first):
1. FORAGE_DJ_DATA_ROOT environment variable
2. .grok/paths.json (written by installers)
3. Platform heuristics (common large drives)
4. Project-local fallback (checkpoints/ and .cache/ inside the repo)

This module is intentionally stdlib-only so it can be imported very early.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

GROK_DIR = PROJECT_ROOT / ".grok"
PATHS_JSON = GROK_DIR / "paths.json"

# ------------------------------------------------------------------
# AUTO-LOAD project cache config so `uv run` "just works"
# without the user having to manually source .grok/hf-cache.env every time.
# This is critical for keeping EVERYTHING inside /mnt/z/IMF2045/forage-dj/
# ------------------------------------------------------------------
def _auto_load_project_env() -> None:
    """Parse .grok/hf-cache.env (export KEY=val style) and set os.environ if not already set."""
    env_file = GROK_DIR / "hf-cache.env"
    if not env_file.exists():
        return
    try:
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Handle "export KEY=val" and "KEY=val"
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Only set if not already in environment (respect explicit user overrides)
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        pass  # never break import

_auto_load_project_env()


def _read_paths_json() -> dict:
    if PATHS_JSON.exists():
        try:
            return json.loads(PATHS_JSON.read_text())
        except Exception:
            pass
    return {}


def _detect_large_drive() -> Optional[Path]:
    """Best-effort detection of a large/fast drive on this machine."""
    system = platform.system()

    if system == "Linux":
        candidates = [
            Path("/mnt/z"),
            Path("/mnt/data"),
            Path("/mnt/fast"),
            Path("/data"),
            Path.home() / "forage-data",
            Path.home() / "Music" / "forage-dj-data",
        ]
        for p in candidates:
            if p.exists() and p.is_dir():
                # Heuristic: prefer if it has > 100GB free or just exists on user's known big drive
                try:
                    usage = shutil.disk_usage(p)
                    if usage.free > 100 * 1024**3:  # >100 GB free
                        return p
                except Exception:
                    return p  # exists is good enough
        return None

    if system == "Windows":
        # Common large drive letters for media / data
        for letter in ["D", "E", "F", "G", "H", "I"]:
            p = Path(f"{letter}:/")
            if p.exists():
                try:
                    usage = shutil.disk_usage(p)
                    if usage.free > 80 * 1024**3:
                        return p / "forage-dj-data"
                except Exception:
                    continue
        # Fallback to user profile
        return Path(os.environ.get("USERPROFILE", str(Path.home()))) / "forage-dj-data"

    # macOS and others
    return Path.home() / "forage-dj-data"


def get_data_root() -> Path:
    """
    Returns the root directory for all large assets (checkpoints, HF cache, libraries, generated audio).
    """
    # 1. Explicit env var (highest priority, great for containers / RunPod / shared setups)
    env_root = os.environ.get("FORAGE_DJ_DATA_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    # 2. paths.json written by installers
    data = _read_paths_json()
    if "data_root" in data:
        return Path(data["data_root"]).expanduser().resolve()

    # 3. Heuristic detection of large drive
    detected = _detect_large_drive()
    if detected:
        return detected.resolve()

    # 4. Safe project-local fallback (works everywhere, just slower on small drives)
    return PROJECT_ROOT / "data"


def get_checkpoints_dir() -> Path:
    root = get_data_root()
    # Keep the historical layout so existing Z: users don't break
    if (PROJECT_ROOT / "checkpoints").exists() and str(root).startswith(str(PROJECT_ROOT / "data")):
        # If user is on classic layout, prefer the existing checkpoints/ dir
        return PROJECT_ROOT / "checkpoints"
    return root / "checkpoints"


def get_hf_home() -> Path:
    """Hugging Face cache location (respects FORAGE_DJ_DATA_ROOT and paths.json)."""
    env = os.environ.get("HF_HOME")
    if env:
        return Path(env).expanduser().resolve()

    data = _read_paths_json()
    if "hf_home" in data:
        return Path(data["hf_home"]).expanduser().resolve()

    return get_data_root() / ".cache" / "huggingface"


def ensure_data_dirs() -> dict:
    """Create the standard data directories and return their paths.
    Includes new 'sessions/' and 'generated/' for the Ableton-style workstation.
    """
    root = get_data_root()
    checkpoints = get_checkpoints_dir()
    libs = root / "libraries"
    generated = root / "generated"
    sessions = root / "sessions"
    sets = PROJECT_ROOT / "setlists"
    test_out = PROJECT_ROOT / "test_outputs"
    comfy_out = get_comfy_output_dir()

    for d in [root, checkpoints, libs, generated, sessions, sets, test_out, comfy_out]:
        d.mkdir(parents=True, exist_ok=True)

    return {
        "data_root": str(root),
        "checkpoints": str(checkpoints),
        "libraries": str(libs),
        "generated": str(generated),
        "sessions": str(sessions),
        "hf_home": str(get_hf_home()),
        "comfy_workflows": str(get_comfy_workflows_dir()),
        "comfy_output": str(comfy_out),
    }


def get_generated_dir() -> Path:
    """Directory for raw generated tracks and variations."""
    return get_data_root() / "generated"


def get_sessions_dir() -> Path:
    """Directory for workstation session projects (like Ableton Live Sets)."""
    return get_data_root() / "sessions"


def get_comfy_workflows_dir() -> Path:
    """Directory containing ComfyUI workflow JSON files used by ForageDJ."""
    return PROJECT_ROOT / "workflows" / "comfy"


def get_comfy_output_dir() -> Path:
    """
    Directory where ComfyUI writes generated audio files.

    Priority:
    1. COMFYUI_OUTPUT_DIR environment variable (explicit override)
    2. <data_root>/comfyui_output
    3. Project-local comfyui_output/ (legacy layout)
    """
    env_dir = os.environ.get("COMFYUI_OUTPUT_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    root = get_data_root()
    candidate = root / "comfyui_output"
    if candidate.exists() or str(root).startswith(str(PROJECT_ROOT)):
        # Prefer data_root version when we control the layout
        return candidate

    # Legacy fallback next to the project
    return PROJECT_ROOT / "comfyui_output"


def write_paths_json(data_root: Optional[Path] = None, hf_home: Optional[Path] = None) -> Path:
    """Write (or update) the machine-local paths.json so Python code finds the right locations."""
    GROK_DIR.mkdir(parents=True, exist_ok=True)

    current = _read_paths_json()
    if data_root:
        current["data_root"] = str(data_root.resolve())
    if hf_home:
        current["hf_home"] = str(hf_home.resolve())

    # Always ensure a data_root
    if "data_root" not in current:
        current["data_root"] = str(get_data_root())

    PATHS_JSON.write_text(json.dumps(current, indent=2))
    return PATHS_JSON


def get_env_activation_hints() -> dict:
    """Return shell snippets the user (or installer) can use to set env vars for the current shell."""
    hf = get_hf_home()
    return {
        "bash": f"export HF_HOME={hf}\nexport HUGGINGFACE_HUB_CACHE={hf}/hub",
        "powershell": f'$env:HF_HOME = "{hf}"\n$env:HUGGINGFACE_HUB_CACHE = "{hf}/hub"',
        "cmd": f'set HF_HOME={hf}\nset HUGGINGFACE_HUB_CACHE={hf}/hub',
    }


if __name__ == "__main__":
    print("forage-dj paths (cross-platform)")
    print("Data root :", get_data_root())
    print("Checkpoints:", get_checkpoints_dir())
    print("HF home   :", get_hf_home())
    print("Hints:\n", get_env_activation_hints())