"""Autonomous agent layer (thin wrapper around sonic-forage-autonomous-dj-os Ralph loop).

Phase 3+. Safety gates are non-negotiable: human approval for any public/booking action.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def run_autonomous_loop(setlist: list[str], seed: int = 42) -> None:
    """High-level 'set it and forget it' mode.

    Future: import ralph from autonomous-dj-os, feed prompts + seed,
    receive suggested transitions, generate on demand, etc.
    """
    logger.warning("Autonomous agent not yet wired (Phase 3).")
    logger.info("You gave me a setlist of %d prompts with seed=%d", len(setlist), seed)
    # TODO (swarm): integrate the real Ralph loop + safety gate
    print("🤖 Autonomous mode coming soon. For now use manual generate + mix.")
