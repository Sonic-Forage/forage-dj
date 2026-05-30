"""Hardware abstraction layer (MIDI + OSC).

Numark NS7II first-class + MIDI Learn + generic controllers.
See docs/HARDWARE_NS7II.md and AGENTIC_BUILD_PLAN Phase 2.
"""

from . import midi, osc  # noqa: F401

__all__ = ["midi", "osc"]
