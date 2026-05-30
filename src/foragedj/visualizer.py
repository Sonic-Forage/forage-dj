"""Poor man's terminal audio visualizer.

Uses Rich + sounddevice + numpy for a beautiful real-time waveform.

Run standalone or integrated with the player.
"""

from __future__ import annotations

import numpy as np
import sounddevice as sd
from collections import deque
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()

SAMPLE_RATE = 44100
HISTORY_LEN = 8192

audio_history = deque(maxlen=HISTORY_LEN)


def audio_callback(indata, frames, time_info, status):
    if status:
        console.print(f"[yellow]{status}[/yellow]")
    mono = indata.mean(axis=1) if indata.ndim > 1 else indata.flatten()
    audio_history.extend(mono.astype(np.float32))


def create_waveform_text(width: int, height: int) -> Text:
    if len(audio_history) < width:
        return Text("Waiting for audio... Play music or speak near the mic", style="dim")

    data = np.array(list(audio_history)[-width * 4:], dtype=np.float32)
    max_amp = np.max(np.abs(data)) + 1e-8
    data = data / max_amp * 0.92

    indices = np.linspace(0, len(data) - 1, width, dtype=int)
    samples = data[indices]

    text = Text()
    center_y = height // 2
    scale = (height // 2 - 2) * 0.95

    for y in range(height):
        line = []
        for x in range(width):
            sample_y = int(center_y - samples[x] * scale)
            diff = abs(y - sample_y)
            if diff == 0:
                line.append("█")
            elif diff == 1:
                line.append("▓")
            elif y == center_y:
                line.append("─")
            else:
                line.append(" ")
        style = "bold bright_cyan" if abs(y - center_y) < 3 else "cyan" if abs(y - center_y) < 6 else "blue"
        text.append("".join(line) + "\n", style=style)
    return text


def run_visualizer():
    """Run the terminal waveform visualizer."""
    console.clear()
    console.print("[bold green]🎤 forage-dj Terminal Waveform Visualizer[/bold green]")
    console.print("Press Ctrl+C to exit\n")

    try:
        with Live(refresh_per_second=30, console=console, screen=True) as live:
            stream = sd.InputStream(
                samplerate=SAMPLE_RATE, channels=1, callback=audio_callback, blocksize=1024, dtype="float32"
            )
            with stream:
                while True:
                    w = max(60, console.width - 6)
                    h = max(10, console.height - 12)
                    live.update(Panel(create_waveform_text(w, h), title="Real-time Waveform"))
    except KeyboardInterrupt:
        console.print("\n[bold red]Visualizer stopped.[/bold red]")