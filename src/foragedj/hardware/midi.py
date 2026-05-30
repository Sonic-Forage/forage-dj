"""Flexible MIDI mapping system for any controller + MIDI Learn.

Supports custom JSON mappings, learn mode, bidirectional feedback (LEDs), and easy binding to mixer parameters or custom callbacks.

Core deps: mido + python-rtmidi (already in base).

Usage example:
    from foragedj.hardware.midi import MidiMapper
    mapper = MidiMapper()
    mapper.bind("deck1.volume", "cc:0:7")  # or use learn mode
    mapper.start()
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from ..utils import MIDI_MAP_PATH

logger = logging.getLogger(__name__)

try:
    import mido
    HAS_MIDO = True
except ImportError:
    HAS_MIDO = False
    logger.warning("mido not available — MIDI support disabled")


class MidiMapper:
    """
    Powerful, learnable MIDI mapper.

    - Dynamic binding of MIDI messages to parameter names or callbacks.
    - MIDI Learn mode (enter learn, move control, it binds).
    - JSON persistence for user mappings.
    - Support for CC, Note, Pitchbend, etc.
    - Easy integration with mixer or any object.
    """

    def __init__(self, port_name: Optional[str] = None):
        self.port_name = port_name
        self.mappings: Dict[str, Dict[str, Any]] = self._load_mapping()
        self._input = None
        self._output = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.learn_target: Optional[str] = None  # param name we're learning for
        self.on_learn: Optional[Callable[[str, str], None]] = None  # callback when learned

        # Default callbacks (user can override or bind directly)
        self.callbacks: Dict[str, Callable[[float], None]] = {}

    def _load_mapping(self) -> dict:
        if MIDI_MAP_PATH.exists():
            try:
                return json.loads(MIDI_MAP_PATH.read_text())
            except Exception as e:
                logger.warning(f"Failed to load MIDI mapping: {e}")
        return {}

    def save_mapping(self) -> None:
        MIDI_MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
        MIDI_MAP_PATH.write_text(json.dumps(self.mappings, indent=2))
        logger.info(f"MIDI mapping saved to {MIDI_MAP_PATH}")

    def bind(self, param_name: str, midi_spec: str, callback: Optional[Callable[[float], None]] = None):
        """
        Bind a parameter to a MIDI control.
        midi_spec formats:
            "cc:0:7"          -> CC channel 0, number 7
            "note:0:60"       -> Note channel 0, note 60
            "pitch:0"         -> Pitch bend channel 0
        """
        self.mappings[param_name] = {"spec": midi_spec}
        if callback:
            self.callbacks[param_name] = callback
        self.save_mapping()
        logger.info(f"Bound {param_name} -> {midi_spec}")

    def unbind(self, param_name: str):
        self.mappings.pop(param_name, None)
        self.callbacks.pop(param_name, None)
        self.save_mapping()

    def start_learn(self, param_name: str, callback: Optional[Callable[[float], None]] = None):
        """Enter learn mode for a specific parameter."""
        self.learn_target = param_name
        if callback:
            self.callbacks[param_name] = callback
        logger.info(f"MIDI Learn active for '{param_name}' — move a control now...")

    def _parse_spec(self, spec: str) -> Tuple[str, int, Optional[int]]:
        parts = spec.split(":")
        msg_type = parts[0]
        channel = int(parts[1])
        number = int(parts[2]) if len(parts) > 2 else None
        return msg_type, channel, number

    def _message_to_value(self, msg) -> Optional[float]:
        if msg.type == "control_change":
            return msg.value / 127.0
        elif msg.type == "note_on":
            return 1.0 if msg.velocity > 0 else 0.0
        elif msg.type == "pitchwheel":
            return (msg.pitch + 8192) / 16383.0
        return None

    def _handle_message(self, msg):
        if not HAS_MIDO:
            return

        # Learn mode
        if self.learn_target and msg.type in ("control_change", "note_on", "pitchwheel"):
            spec = f"{msg.type}:{msg.channel}"
            if hasattr(msg, "control"):
                spec += f":{msg.control}"
            elif hasattr(msg, "note"):
                spec += f":{msg.note}"

            self.mappings[self.learn_target] = {"spec": spec}
            self.save_mapping()

            if self.on_learn:
                self.on_learn(self.learn_target, spec)

            logger.info(f"Learned {self.learn_target} -> {spec}")
            self.learn_target = None
            return

        # Normal dispatch
        for param, data in list(self.mappings.items()):
            spec = data.get("spec", "")
            try:
                msg_type, ch, num = self._parse_spec(spec)
                if msg.type != msg_type or msg.channel != ch:
                    continue
                if num is not None and hasattr(msg, "control") and msg.control != num:
                    continue
                if num is not None and hasattr(msg, "note") and msg.note != num:
                    continue

                value = self._message_to_value(msg)
                if value is not None:
                    if param in self.callbacks:
                        self.callbacks[param](value)
                    else:
                        logger.debug(f"MIDI {param} = {value:.3f} (no callback registered)")
            except Exception as e:
                logger.debug(f"MIDI mapping error for {param}: {e}")

    def start(self):
        if not HAS_MIDO:
            logger.error("mido not installed")
            return

        try:
            ports = mido.get_input_names()
            if not ports:
                logger.warning("No MIDI input ports found")
                return

            name = self.port_name or ports[0]
            self._input = mido.open_input(name)
            logger.info(f"Listening on MIDI port: {name}")

            self._running = True
            self._thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._thread.start()

        except Exception as e:
            logger.error(f"MIDI start failed: {e}")

    def _listen_loop(self):
        while self._running and self._input:
            for msg in self._input.iter_pending():
                self._handle_message(msg)
            # Small sleep to avoid busy loop
            import time
            time.sleep(0.001)

    def stop(self):
        self._running = False
        if self._input:
            self._input.close()
        if self._thread:
            self._thread.join(timeout=1)

    def list_ports(self):
        if HAS_MIDO:
            return mido.get_input_names()
        return []


# Backwards compat
def get_controller(device: str = "ns7ii") -> MidiMapper:
    return MidiMapper()
