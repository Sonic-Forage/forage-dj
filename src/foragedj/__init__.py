"""Sonic Forage DJ - AI-powered autonomous DJ interface/DAW

Public-safe by default. Harm reduction and prompt provenance baked in.
See docs/WHITEPAPER.md and the Sonic Forage mycelium for culture.
"""

__version__ = "0.1.0"

# Lazy / guarded imports so `uv run foragedj` and `import foragedj` succeed
# even when optional extras (gui, gen, voice, stems) are not installed.
# Real implementations live in the sibling modules (see ARCHITECTURE.md).

from . import cli  # always safe

__all__ = ["__version__", "cli"]

# The following become available after the corresponding extras are installed
# or when the modules are implemented:
#   from foragedj import audio_gen, mixer, analysis, gui, voice, agent, utils
#   from foragedj.hardware import midi, osc
