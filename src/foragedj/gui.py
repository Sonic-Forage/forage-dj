"""Dear PyGui interface (minimal 2-deck MVP).

Per ARCHITECTURE, FEATURES_SPEC P0, and swarm agent 019e7a00-4c1a-7ba0-bb9a-860ec237b7c4
(archived in .grok/swarm-outputs/).

This is a small but fully launchable + wired UI based on the agent's "smallest viable"
layout recommendation. Extendable in <2 hours.
"""

from __future__ import annotations

import logging
from functools import partial

logger = logging.getLogger(__name__)

try:
    import dearpygui.dearpygui as dpg
    HAS_GUI = True
except ImportError:
    HAS_GUI = False


def launch() -> None:
    """Launch the minimal 2-deck Dear PyGui interface (blocking)."""
    if not HAS_GUI:
        raise RuntimeError("Dear PyGui not installed. Run: uv sync --extra gui")

    from .mixer import Mixer
    from .audio_gen import generate_track

    mixer = Mixer()

    dpg.create_context()
    dpg.create_viewport(title="forage-dj — Phase 1 MVP", width=1100, height=620)
    dpg.setup_dearpygui()

    with dpg.window(label="forage-dj", tag="main", width=1080, height=580):
        dpg.add_text("Sonic Forage AI DJ — 2 Deck (swarm skeleton from agent 019e7a00-4c1a...)")
        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_button(label="Auto Mix (stub)")
            dpg.add_text("Crossfader")
            dpg.add_slider_float(tag="crossfader", min_value=-1.0, max_value=1.0,
                                 default_value=0.0, width=400,
                                 callback=lambda s, a: mixer.set_crossfader(a))

        with dpg.group(horizontal=True):
            for deck_id in (1, 2):
                with dpg.group():
                    dpg.add_text(f"Deck {deck_id}")
                    dpg.add_input_text(tag=f"prompt{deck_id}", default_value="dark techno 128bpm", width=420)
                    dpg.add_button(label="Diffuse / Generate",
                                   callback=partial(_do_generate, deck_id, mixer))
                    dpg.add_progress_bar(tag=f"progress{deck_id}", default_value=0.0, width=420)

                    dpg.add_separator()
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="▶", callback=lambda: mixer.play(deck_id))
                        dpg.add_button(label="⏸", callback=lambda: mixer.pause(deck_id))
                        dpg.add_button(label="Cue", callback=lambda: setattr(
                            mixer.deck1 if deck_id == 1 else mixer.deck2, "position", 0.0))

                    dpg.add_slider_float(label="Volume", min_value=0.0, max_value=1.0,
                                         default_value=0.8, tag=f"vol{deck_id}", width=300,
                                         callback=partial(_update_deck_param, mixer, deck_id, "volume"))
                    dpg.add_slider_float(label="EQ Low", min_value=-12, max_value=12,
                                         tag=f"eq_low{deck_id}", width=300,
                                         callback=partial(_update_deck_param, mixer, deck_id, "eq_low"))
                    dpg.add_slider_float(label="EQ Mid", min_value=-12, max_value=12,
                                         tag=f"eq_mid{deck_id}", width=300,
                                         callback=partial(_update_deck_param, mixer, deck_id, "eq_mid"))
                    dpg.add_slider_float(label="EQ High", min_value=-12, max_value=12,
                                         tag=f"eq_high{deck_id}", width=300,
                                         callback=partial(_update_deck_param, mixer, deck_id, "eq_high"))
                    dpg.add_slider_float(label="Filter (Hz)", min_value=20, max_value=20000,
                                         default_value=20000, tag=f"filt{deck_id}", width=300,
                                         callback=partial(_update_deck_param, mixer, deck_id, "filter_cutoff"))

                    dpg.add_text(tag=f"bpm{deck_id}", default_value="BPM: --  Key: --")

        dpg.add_separator()
        dpg.add_text(tag="status", default_value="Ready — use prompts above or CLI 'generate'")

    dpg.show_viewport()

    def _poll():
        state = mixer.get_state()
        for did in (1, 2):
            d = state[f"deck{did}"]
            dpg.set_value(f"bpm{did}", f"BPM: {d['bpm']}  Key: {d.get('key', '--')}")
        dpg.set_value("status", f"Crossfader: {state['crossfader']:.2f} | Running: {mixer._stream is not None}")

    while dpg.is_dearpygui_running():
        _poll()
        dpg.render_dearpygui_frame()

    dpg.destroy_context()


def _update_deck_param(mixer, deck_id, param, sender, app_data):
    d = mixer.deck1 if deck_id == 1 else mixer.deck2
    setattr(d, param, app_data)


def _do_generate(deck_id, mixer, sender=None, app_data=None):
    prompt = dpg.get_value(f"prompt{deck_id}")
    dpg.set_value(f"progress{deck_id}", 0.0)

    def _progress(p, msg):
        dpg.set_value(f"progress{deck_id}", p)
        dpg.set_value("status", f"Deck {deck_id}: {msg}")

    try:
        path = generate_track(prompt, seed=42 + deck_id, progress_callback=_progress)
        mixer.load_deck(deck_id, path)
        dpg.set_value("status", f"Deck {deck_id} loaded: {path.name}")
        mixer.start()
    except Exception as e:
        dpg.set_value("status", f"Error on generate: {e}")
