"""Simple configuration system for forage-dj.

Supports lookahead, realtime mode, model preferences, etc.
Stored in ~/.foragedj/config.json (or project-local override).
"""

from __future__ import annotations

import json
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


config = load_config()
