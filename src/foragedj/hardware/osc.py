"""OSC support for Resolume, TouchOSC, and custom controllers.

Full bidirectional support using python-osc.

Resolume example addresses (use Resolume's "Edit OSC" mode to discover exact paths for your comp):
- /composition/layers/1/clips/1/connect 1          → trigger clip
- /composition/layers/1/video/opacity 0.75         → set opacity
- /composition/layers/1/speed 1.0                  → speed
- /composition/crossfader 0.5

Usage:
    from foragedj.hardware.osc import OSCBridge
    bridge = OSCBridge()
    bridge.map("/composition/layers/1/video/opacity", lambda v: mixer.set_master_opacity(v))
    bridge.start()
"""

from __future__ import annotations

import logging
import threading
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from pythonosc.dispatcher import Dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.udp_client import SimpleUDPClient
    HAS_OSC = True
except ImportError:
    HAS_OSC = False
    logger.warning("python-osc not installed. Install with: uv pip install python-osc")


class OSCBridge:
    """
    Bidirectional OSC bridge.

    - Server: receives from controllers / Resolume feedback
    - Client: sends to Resolume / visualizers / TouchOSC
    - Easy mapping of OSC addresses to Python callbacks
    - Great for syncing DJ actions to video (Resolume) or vice versa.
    """

    def __init__(self, listen_ip: str = "0.0.0.0", listen_port: int = 9000,
                 send_ip: str = "127.0.0.1", send_port: int = 7000):
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.send_ip = send_ip
        self.send_port = send_port

        self.mappings: Dict[str, Callable] = {}
        self._server: Optional[ThreadingOSCUDPServer] = None
        self._client: Optional[SimpleUDPClient] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def map(self, address: str, callback: Callable[[float | str], None]):
        """Map an OSC address to a callback. Value is usually float 0-1."""
        self.mappings[address] = callback

    def send(self, address: str, value: float | str | int):
        """Send a value to the target (e.g. Resolume)."""
        if not self._client:
            return
        self._client.send_message(address, value)

    def _handle_message(self, address: str, *args):
        if address in self.mappings:
            try:
                val = args[0] if args else 0
                self.mappings[address](val)
            except Exception as e:
                logger.error(f"OSC callback error for {address}: {e}")
        else:
            logger.debug(f"Unhandled OSC: {address} {args}")

    def start(self):
        if not HAS_OSC:
            logger.error("python-osc not available. Run: uv pip install python-osc")
            return

        try:
            dispatcher = Dispatcher()
            dispatcher.map("/*", self._handle_message)  # catch all, we filter inside

            self._server = ThreadingOSCUDPServer((self.listen_ip, self.listen_port), dispatcher)
            self._client = SimpleUDPClient(self.send_ip, self.send_port)

            self._running = True
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()

            logger.info(f"OSC listening on {self.listen_ip}:{self.listen_port}, sending to {self.send_ip}:{self.send_port}")

        except Exception as e:
            logger.error(f"OSC start failed: {e}")

    def stop(self):
        self._running = False
        if self._server:
            self._server.shutdown()
        if self._thread:
            self._thread.join(timeout=1)
        logger.info("OSC stopped")


# Convenience factory for common Resolume use case
def create_resolume_bridge(resolume_ip: str = "127.0.0.1", resolume_port: int = 7000,
                           listen_port: int = 9001) -> OSCBridge:
    """Pre-configured bridge for talking to Resolume."""
    return OSCBridge(listen_port=listen_port, send_ip=resolume_ip, send_port=resolume_port)
