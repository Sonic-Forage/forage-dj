"""
Avaturn Reactive Avatar Integration Stub for Sonic Forage

Goal: Characters that listen to the music (via our analysis + workstation features),
bob/dance/react in real time, show small UI encouragement, and help people create
their own tuned avatars.

This is the beginning. We can feed:
- BPM, energy, key, onset strength from analysis.py
- Current region prompt + emotional tone
- Workstation regeneration events (big visual reactions when a region changes)

Future: Fine-tune models on our local generated + performed music dataset.

All code stays inside /mnt/z/IMF2045/forage-dj/
"""

from pathlib import Path
from typing import Optional

class AvaturnAvatar:
    def __init__(self, character_id: str, model_path: Optional[Path] = None):
        self.character_id = character_id
        self.model_path = model_path
        self.current_energy = 0.5
        self.current_emotion = "neutral"

    def update_from_music(self, bpm: float, energy: float, key: str, prompt: str):
        """Call this every few seconds from the mixer or workstation."""
        self.current_energy = energy
        # Simple heuristic for now — replace with real model later
        if energy > 0.7:
            self.current_emotion = "hype"
        elif "dark" in prompt.lower() or "reese" in prompt.lower():
            self.current_emotion = "intense"
        else:
            self.current_emotion = "groove"

        print(f"[Avaturn] {self.character_id} reacting — energy={energy:.2f} emotion={self.current_emotion}")

    def get_ui_overlay_text(self) -> str:
        """Small pop-up text the avatar can show to encourage creation."""
        if self.current_energy > 0.8:
            return "This drop is hitting different 🔥 Want to make your own avatar?"
        return "Listening with you... Create your own character?"

    # TODO: Real integration with Avaturn API / avtr-1
    # TODO: OSC bridge to drive external avatar software from our audio features
    # TODO: Dataset collection pipeline for fine-tuning on our local music


if __name__ == "__main__":
    avatar = AvaturnAvatar("demo-dancer")
    avatar.update_from_music(bpm=128, energy=0.85, key="Am", prompt="filthy rolling reese bass")
    print(avatar.get_ui_overlay_text())
