"""AI DJ Personalities System for Sonic Forage

Loads customizable DJ personalities with strong music taste profiles.
Used for autonomous sets, chat bots, promotional characters ("Rex"), etc.

All data lives in data/ai_dj_personalities/personalities.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
PERSONALITIES_PATH = PROJECT_ROOT / "data" / "ai_dj_personalities" / "personalities.json"


class DJPersonality:
    def __init__(self, data: Dict):
        self.name = data["name"]
        self.dj_name = data.get("dj_name", self.name)
        self.favorite_styles = data.get("favorite_styles", [])
        self.disliked_styles = data.get("disliked_styles", [])
        self.personality = data.get("personality", "")
        self.catchphrases = data.get("catchphrases", [])
        self.vibe = data.get("vibe", "")

    def describe(self) -> str:
        return f"{self.dj_name} — {self.vibe}. Loves: {', '.join(self.favorite_styles[:3])}. Dislikes: {', '.join(self.disliked_styles[:2])}."

    def get_prompt_fragment(self) -> str:
        """Returns a string suitable for injecting into an AI prompt."""
        return (
            f"You are {self.dj_name}, a {self.vibe} DJ. "
            f"You love {', '.join(self.favorite_styles[:4])}. "
            f"You hate {', '.join(self.disliked_styles[:2])}. "
            f"Your personality: {self.personality}. "
            f"Use phrases like: {' / '.join(self.catchphrases[:2])}"
        )


def load_personalities() -> Dict[str, DJPersonality]:
    """Load all personalities from the JSON file."""
    if not PERSONALITIES_PATH.exists():
        raise FileNotFoundError(f"Personalities file not found: {PERSONALITIES_PATH}")

    data = json.loads(PERSONALITIES_PATH.read_text())
    personalities = {}
    for p in data.get("personalities", []):
        personalities[p["name"]] = DJPersonality(p)
    return personalities


def get_personality(name: str) -> Optional[DJPersonality]:
    """Get a specific personality by name (case sensitive)."""
    all_p = load_personalities()
    return all_p.get(name)


def list_personalities() -> List[str]:
    """Return list of available personality names."""
    return list(load_personalities().keys())


def get_random_personality() -> DJPersonality:
    """Pick a random personality (useful for autonomous sets)."""
    import random
    all_p = load_personalities()
    return random.choice(list(all_p.values()))


if __name__ == "__main__":
    print("Sonic Forage AI DJ Personalities")
    print("Available:", list_personalities())
    print()
    p = get_personality("Neon")
    if p:
        print(p.describe())
        print(p.get_prompt_fragment())
