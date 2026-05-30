"""Voice interface (STT + local LLM intent parsing).

Phase 2. Uses faster-whisper (tiny) + Ollama or similar.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def listen_and_route(
    hotword: str = "forage",
    callback: Optional[callable] = None,
) -> None:
    """Start always-on or push-to-talk listener. Routes parsed intent to actions."""
    try:
        import faster_whisper  # type: ignore  # noqa: F401
    except ImportError:
        raise RuntimeError("Voice support requires: uv sync --extra voice") from None

    logger.info("Voice stub — real STT + LLM routing is Phase 2 swarm work")
    # TODO: whisper model, mic stream, Ollama prompt for intent, dispatch to mixer/agent
