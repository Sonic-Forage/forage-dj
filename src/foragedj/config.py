"""Simple configuration system for forage-dj.

Supports lookahead, realtime mode, model preferences, etc.
Stored in ~/.foragedj/config.json (or project-local override).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "live": {
        "default_lookahead": 2,
        "realtime_enabled": False,
        "preferred_model": "small-music",
    },
    "generation": {
        "max_duration": 120,
        "cpu_friendly": True,
        "default_backend": "comfy",           # "comfy" (primary - ACE-Step 1.5 XL Turbo etc. via ComfyUI, local or remote) | "python" (legacy, see legacy/stable-audio-python branch)
        "comfy_url": None,                    # Override for COMFYUI_URL env var (e.g. http://100.99.10.17:8188 or your RunPod URL)
    },
    "terminal": {
        "theme": "dark",
        "show_energy": True,
    },
}

CONFIG_DIR = Path.home() / ".foragedj"
CONFIG_PATH = CONFIG_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        try:
            user_config = json.loads(CONFIG_PATH.read_text())
            # Deep merge (simple version)
            config = DEFAULT_CONFIG.copy()
            for section, values in user_config.items():
                if section in config:
                    config[section].update(values)
                else:
                    config[section] = values
            return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2))


def get_default_backend() -> str:
    """Returns the configured default backend.
    'comfy' is now the primary path (ACE-Step / other ComfyUI audio workflows, local or remote).
    'python' (Stable Audio 3) is legacy and lives on the legacy/stable-audio-python branch.
    """
    cfg = load_config()
    backend = cfg.get("generation", {}).get("default_backend", "comfy")
    return str(backend).lower()


def get_comfy_url() -> str | None:
    """Returns the configured ComfyUI URL (from config or falls back to env)."""
    cfg = load_config()
    url = cfg.get("generation", {}).get("comfy_url")
    if url:
        return str(url)
    return os.environ.get("COMFYUI_URL")


def set_default_backend(backend: str, comfy_url: str | None = None) -> None:
    """
    Easy one-liner to switch defaults.

    Example:
        from src.foragedj.config import set_default_backend
        set_default_backend("comfy", "http://100.99.10.17:8188")
    """
    cfg = load_config()
    cfg.setdefault("generation", {})
    cfg["generation"]["default_backend"] = backend.lower()
    if comfy_url:
        cfg["generation"]["comfy_url"] = comfy_url
    save_config(cfg)
    print(f"✅ Default backend set to '{backend}' in ~/.foragedj/config.json")


config = load_config()
