"""
Rex Intro Script Generator

Uses Sonic Forage AI DJ Personalities to generate fun, on-brand scripts
for HeyGen HyperFrames / interactive video.

Example:
    uv run python integrations/hyperframes/scripts/rex_intro.py Neon
"""

import sys
from pathlib import Path

# Make sure we can import from the project
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from foragedj.personalities import get_personality


def generate_rex_script(personality_name: str) -> str:
    p = get_personality(personality_name)
    if not p:
        return f"Personality '{personality_name}' not found."

    script = f"""[REX INTRO - {p.dj_name}]

Hey... I'm Rex. Not the dinosaur. The one who lives in the machines.

Tonight we're doing something a little illegal in spirit.

We're using Sonic Forage — this weird local AI music thing — to generate, edit, and destroy music in real time.

{p.get_prompt_fragment()}

So if the bass feels like it's talking to you... it probably is.

Welcome to the mycelium.

Stay hydrated. PLUR is real. And whatever you do tonight — make it beautiful and slightly dangerous.
"""
    return script


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "Neon"
    print(generate_rex_script(name))
