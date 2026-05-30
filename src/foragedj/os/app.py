"""
forage-dj OS - Retro Terminal Operating System

Boot into a full "computer" interface for the entire project.
Old school aesthetic + modern power.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Label
from textual.screen import Screen
from rich.text import Text

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()

class BootScreen(Screen):
    """Cool retro boot sequence with logo."""

    def compose(self) -> ComposeResult:
        yield Static("", id="boot_log")

    async def on_mount(self) -> None:
        log = self.query_one("#boot_log", Static)
        boot_lines = [
            "SONIC FORAGE BIOS v0.1.0 - 2026",
            "Initializing Z: drive filesystem...",
            "Loading AI audio core...",
            "Mounting checkpoints/ ... OK",
            "Mounting setlists/ ... OK",
            "Detecting GPU...",
            "RTX 4070 detected - 12GB VRAM",
            "Booting Music Diffusion OS...",
            "",
            "   ███████╗ ██████╗ ███╗   ██╗██╗ ██████╗",
            "   ██╔════╝██╔═══██╗████╗  ██║██║██╔════╝",
            "   ███████╗██║   ██║██╔██╗ ██║██║██║     ",
            "   ╚════██║██║   ██║██║╚██╗██║██║██║     ",
            "   ███████║╚██████╔╝██║ ╚████║██║╚██████╗",
            "   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝",
            "",
            "   FORAGE-DJ - The First Music Diffusion OS",
            "",
            "Press any key to enter desktop...",
        ]

        for line in boot_lines:
            log.update(Text.from_markup(line + "\n"))
            await asyncio.sleep(0.08)

        # Wait for keypress
        await self.app.wait_for_keypress()


class Desktop(Screen):
    """Old school desktop with icons."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="desktop"):
            yield Label("🍓 SONIC FORAGE OS - Z: Drive", id="title")
            with Horizontal(id="icons"):
                yield Button("🎵  Player", id="player", variant="primary")
                yield Button("🚀  Live DJ", id="live", variant="success")
                yield Button("📜  Setlists", id="setlists", variant="primary")
                yield Button("👁️  Visualizer", id="viz", variant="default")
                yield Button("🎛️  Controllers", id="controllers", variant="warning")
                yield Button("🧠  Agent Lab", id="agents", variant="error")
                yield Button("🔊  Enhancer", id="enhancer", variant="primary")
                yield Button("🗣️  Voice Lab", id="voicelab", variant="success")
                yield Button("🎚️  Workstation", id="workstation", variant="primary")
                yield Button("⚙️  System", id="system", variant="default")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "player":
            self.app.push_screen(PlayerApp())
        elif event.button.id == "live":
            self.app.push_screen(LiveDJScreen())
        elif event.button.id == "viz":
            self.app.push_screen(VisualizerScreen())
        elif event.button.id == "system":
            self.app.push_screen(SystemScreen())
        elif event.button.id == "enhancer":
            self.app.push_screen(EnhancerLabScreen())
        elif event.button.id == "voicelab":
            self.app.push_screen(VoiceLabScreen())
        elif event.button.id == "workstation":
            self.app.push_screen(WorkstationScreen())
        # Add more screens as we build them


class PlayerApp(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Library Player (Winamp mode)\n\nComing soon: full TUI player with your libraries", id="content")
        yield Footer()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()


class LiveDJScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("LIVE AUTONOMOUS DJ\n\nSelect a manifest and go autonomous.\nThis will be wired to the real live command.", id="content")
        yield Footer()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()


class VisualizerScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Terminal Visualizer\n\nPress V to launch the rich waveform visualizer", id="content")
        yield Footer()

    def on_key(self, event) -> None:
        if event.key.lower() == "v":
            from ...visualizer import run_visualizer
            self.app.exit()  # Exit TUI to run the visualizer
            run_visualizer()
        if event.key == "escape":
            self.app.pop_screen()


class SystemScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("System Status\n\nRun 'foragedj doctor --heal' from terminal for full self-healing report.\n\nGPU: RTX 4070\nEverything on Z: drive.", id="content")
        yield Footer()

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()


class EnhancerLabScreen(Screen):
    """Retro audio super-resolution / enhancement station."""

    def compose(self) -> ComposeResult:
        yield Header()
        content = (
            "🔊 ENHANCER LAB — Sonic Forage Audio Super-Resolution\n\n"
            "FlashSR tiny   → 200-400x realtime 16k→48kHz (tiny files, perfect for live)\n"
            "FlashSR one-step (2025) → excellent quality/speed balance\n"
            "AudioSR (drbaph) → highest quality latent diffusion (slower, max fidelity)\n\n"
            "Usage from terminal:\n"
            "  foragedj enhance my_track.wav --model flashsr-tiny\n"
            "  foragedj enhance final.wav --model audiosr\n\n"
            "Also available: foragedj split-stems (Demucs) for vocal/instrument isolation.\n\n"
            "Models live in checkpoints/enhancers/\n"
            "Run download-models --group enhancers if empty.\n\n"
            "Press E to run a quick example enhance on test_outputs (if present)."
        )
        yield Static(content, id="content")
        yield Footer()

    def on_key(self, event) -> None:
        if event.key.lower() == "e":
            # Quick demo hook — could call the real enhance in future
            print("\n[Enhancer] Launching example enhance via CLI (see terminal output)...\n")
            self.app.exit()
            os.system("uv run foragedj enhance --help || true")
        if event.key == "escape":
            self.app.pop_screen()


class VoiceLabScreen(Screen):
    """Voice tools: cleaning + TTS generation."""

    def compose(self) -> ComposeResult:
        yield Header()
        content = (
            "🗣️ VOICE LAB — LocalVQE + Kokoro TTS\n\n"
            "LocalVQE (LocalAI-io)\n"
            "  Tiny real-time CPU model: echo cancellation + noise suppression + dereverb\n"
            "  5-10x realtime on commodity CPU. GGUF weights in checkpoints/voice/localvqe/\n"
            "  Command: foragedj clean-voice mic_recording.wav --ref far_end.wav\n\n"
            "Kokoro-82M (hexgrad)\n"
            "  82M param Apache TTS — surprisingly high quality + fast streaming\n"
            "  Many voices (af_heart, am_michael, etc.). Perfect for drops, announcements, vocal layers.\n"
            "  Command: foragedj speak \"welcome to the bassline dominion\" --voice af_heart\n\n"
            "First time Kokoro use: uv pip install kokoro soundfile + install espeak-ng\n\n"
            "Press S to test speak from here (simple demo)."
        )
        yield Static(content, id="content")
        yield Footer()

    def on_key(self, event) -> None:
        if event.key.lower() == "s":
            print("\n[Voice Lab] Demo speak — exiting TUI to run CLI...\n")
            self.app.exit()
            os.system('uv run foragedj speak "sonic forage voice lab online" --voice af_heart || true')
        if event.key == "escape":
            self.app.pop_screen()


class WorkstationScreen(Screen):
    """Ableton-style workstation entry point — now with bad-ass visual arranger."""

    def compose(self) -> ComposeResult:
        yield Header()
        content = (
            "🎚️ SONIC FORAGE WORKSTATION — Ableton-like AI Editing (Bad Ass Mode)\n\n"
            "Full diffusion-powered DAW inside your terminal + retro OS.\n\n"
            "What you can do right now:\n"
            "  • Create sessions that live forever on your mounted drive\n"
            "  • Auto-split tracks into musical regions using onset detection\n"
            "  • Regenerate any region with new prompts (smart context from neighbors + auto-enhance)\n"
            "  • Inpaint sections\n"
            "  • See a gorgeous terminal arrangement view (the money feature)\n\n"
            "Power commands:\n"
            "  foragedj workstation-new \"My Insane Drop\"\n"
            "  foragedj workstation-split \"My Insane Drop\" track_01\n"
            "  foragedj workstation-view \"My Insane Drop\"     ←  THIS IS THE ONE (looks pro as hell)\n"
            "  foragedj workstation-regenerate ... \"new darker prompt\"\n\n"
            "The visualizer shows colored region timelines, BPM/Key, full prompts, and lock status.\n\n"
            "Press V to demo the bad-ass arrangement view right now."
        )
        yield Static(content, id="content")
        yield Footer()

    def on_key(self, event) -> None:
        if event.key.lower() == "v":
            print("\n[Workstation] Launching the bad-ass visual arranger demo...\n")
            self.app.exit()
            os.system("uv run foragedj workstation-view \"Test_Ableton_Style_Session\" 2>/dev/null || uv run python -c 'from src.foragedj.workstation import Session, render_session_arrangement; s=Session(name=\"QuickDemo\"); t=s.add_track(\"/mnt/z/IMF2045/forage-dj/libraries/Bassline_Dominion_House_Ignition_Seed424242/01_424242.wav\"); t.add_region(0,16,\"Intro pads\"); t.add_region(16,32,\"Main groove\"); render_session_arrangement(s)' || true")
        if event.key == "escape":
            self.app.pop_screen()


class ForageOS(App):
    """The main OS application."""

    CSS = """
    Screen {
        background: #001100;
        color: #00ff00;
    }
    #title {
        text-align: center;
        padding: 2;
        background: #003300;
    }
    Button {
        width: 20;
        height: 3;
        margin: 1;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(BootScreen())

    def on_key(self, event) -> None:
        if event.key == "d":
            self.push_screen(Desktop())

    def on_screen_dismiss(self, screen: Screen) -> None:
        if isinstance(screen, BootScreen):
            self.push_screen(Desktop())


def run_os():
    """Entry point to boot the OS."""
    app = ForageOS()
    app.run()
