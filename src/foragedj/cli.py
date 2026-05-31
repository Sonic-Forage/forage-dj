"""CLI entrypoint for forage-dj.

Subcommands match TESTING_GUIDE.md and AGENTIC_BUILD_PLAN expectations.
Safe imports + actionable doctor command = excellent first-run experience.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Import paths FIRST — this auto-loads .grok/hf-cache.env so all caches
# (HF + uv) are forced to stay inside /mnt/z/IMF2045/forage-dj/
from . import paths  # noqa: F401  (side-effect: auto-pins caches)

from . import __version__
from .utils import setup_logging

def _print_banner() -> None:
    print(r"""
   ███████╗ ██████╗ ███╗   ██╗██╗ ██████╗
   ██╔════╝██╔═══██╗████╗  ██║██║██╔════╝
   ███████╗██║   ██║██╔██╗ ██║██║██║     
   ╚════██║██║   ██║██║╚██╗██║██║██║     
   ███████║╚██████╔╝██║ ╚████║██║╚██████╗
   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝

   🎛️  SONIC FORAGE — Music Diffusion Workstation
   """)
    print(f"v{__version__} — Everything local on your drive. Editable. Live. Autonomous.")
    print("https://github.com/Sonic-Forage/forage-dj")
    print()
    print("Choose your experience:")
    print("  1. Autonomous DJ (curated, walk-away sets)")
    print("  2. Workstation (edit, regenerate, inpaint regions)")
    print("  3. Streamer Mode (Twitch/Kick ready + chat control)")
    print("  4. Collective (share music, royalties, community)")
    print("  5. Full Custom (build your own thing)")
    print()
    print("Or just run commands directly. Type `foragedj --help` anytime.")


def cmd_version(args: argparse.Namespace) -> None:
    print(f"forage-dj {__version__}")


def cmd_doctor(args: argparse.Namespace) -> None:
    """Comprehensive self-healing system health check."""
    from .health import run_full_health_check

    fix = getattr(args, "heal", False) or getattr(args, "fix", False)
    run_full_health_check(fix=fix)


def cmd_generate(args: argparse.Namespace) -> None:
    from .audio_gen import generate_track

    print(f"🎵 Generating: '{args.prompt}'  seed={args.seed}  dur={args.duration}s  model={args.model}")
    if args.dry:
        print("   (dry run — no actual generation)")
        print("   Would call generate_track(...) and save inside the project (generated/ on Z: drive)")
        return

    try:
        path = generate_track(
            prompt=args.prompt,
            seed=args.seed,
            duration=args.duration,
            model=args.model,
        )
        print(f"✅ Saved: {path}")
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def cmd_gui(args: argparse.Namespace) -> None:
    from .gui import launch
    launch()


def cmd_mix(args: argparse.Namespace) -> None:
    print("🎚️  2-deck mixer (Phase 1 work in progress)")
    print(f"   Would load {args.deck1} + {args.deck2} and crossfade {args.crossfade} bars")
    print("   Real engine lives in src/foragedj/mixer.py (stub ready for swarm)")


def cmd_midi_learn(args: argparse.Namespace) -> None:
    from .hardware.midi import get_controller
    ctrl = get_controller()
    # Use the actual method name that exists on MidiMapper
    if hasattr(ctrl, "start_learn"):
        ctrl.start_learn(args.control or "volume")
    else:
        ctrl.learn(args.control or "volume")  # fallback if someone adds learn() later
    print("MIDI Learn mode — move the hardware control now (see hardware/midi.py for implementation)")


def cmd_generate_setlist(args: argparse.Namespace) -> None:
    from .setlist import generate_setlist

    manifest = Path(args.manifest)
    if not manifest.exists():
        print(f"Manifest not found: {manifest}")
        return

    print(f"🎵 Generating full setlist from manifest: {manifest}")
    print("   (Full walk-away mode: ETA + resume + playlist.txt + harmonic guide. Go make coffee.)")

    library = generate_setlist(
        manifest,
        output_root=Path("libraries"),
        dry=args.dry,
    )

    print(f"\n📁 Library ready at: {library.library_dir}")
    print("   • library.json — full metadata, energy estimates, recommended transitions")
    print("   • playlist.txt — simple text list for Traktor / Serato / Rekordbox / Engine DJ import")
    print("   Open the JSON to see Camelot wheel suggestions + energy arc for your set.")


def cmd_play_library(args: argparse.Namespace) -> None:
    """Basic library player / viewer (Winamp vibes)."""
    from rich.console import Console
    from rich.table import Table
    import json
    from pathlib import Path as _Path

    console = Console()
    lib_dir = _Path(args.library_dir)
    json_path = lib_dir / "library.json"

    if not json_path.exists():
        console.print(f"[red]No library.json found in {lib_dir}[/red]")
        return

    data = json.loads(json_path.read_text())
    tracks = data.get("tracks", [])

    console.print(f"\n[bold magenta]🍓 Library: {data.get('name', lib_dir.name)}[/bold magenta]")
    console.print(f"Seed: {data.get('seed')} | Tracks: {len(tracks)}\n")

    table = Table()
    table.add_column("#")
    table.add_column("File")
    table.add_column("BPM")
    table.add_column("Key")

    for i, t in enumerate(tracks, 1):
        table.add_row(str(i), t.get("file", ""), str(t.get("bpm", "")), t.get("key", ""))

    console.print(table)
    console.print("\n[dim]Full details + harmonic suggestions in library.json[/dim]")


def cmd_download_models(args: argparse.Namespace) -> None:
    """One-command downloader for core + enhancers (FlashSR/AudioSR) + voice tools (LocalVQE/Kokoro)."""
    import subprocess
    import os
    from pathlib import Path as _Path

    print("🍓 forage-dj Full Model + Enhancement + Voice Downloader (Z: drive edition)")
    print("Core SA3 + Sonic-Forage LoRAs + new 2025 stack: FlashSR, AudioSR, LocalVQE, Kokoro notes.\n")
    print("Tip: uv run foragedj download-models will now grab everything by default (use --group in the script for subsets).\n")

    # Auto-source cache + optional local token file for maximum convenience
    cache_env = _Path(".grok/hf-cache.env")
    token_env = _Path(".grok/hf-token.env")

    if cache_env.exists():
        print("→ Sourcing Z: drive cache config...")
        os.system(f"source {cache_env} 2>/dev/null || true")

    if token_env.exists():
        print("→ Sourcing local HF token (from .grok/hf-token.env)...")
        os.system(f"source {token_env} 2>/dev/null || true")

    token = os.environ.get("HF_TOKEN")

    if not token:
        print("\n⚠️  No HF_TOKEN detected — downloads will be slow (unauthenticated rate limits).")
        print("   This is why it's 'taking forever' right now.")
        print("\n   Quick fix (run these commands):")
        print("     export HF_TOKEN=hf_your_token_here")
        print("     # or create a local file (recommended, never commit it):")
        print("     echo 'export HF_TOKEN=hf_your_token_here' > .grok/hf-token.env")
        print("     chmod 600 .grok/hf-token.env")
        print("\n   Then re-run: uv run foragedj download-models")
        print("   See docs/MODEL_ACCESS.md for full gated license + token instructions.\n")
    else:
        print("✅ HF_TOKEN detected — you should get fast authenticated downloads.\n")

    script = _Path("scripts/download_checkpoints.py")
    if not script.exists():
        print("scripts/download_checkpoints.py not found.")
        return

    try:
        env = {**os.environ}
        if token:
            env["HF_TOKEN"] = token
        subprocess.run(["uv", "run", "python", str(script)], check=True, env=env)
        print("\n✅ Downloads complete or resumed. Check checkpoints/ (including loras/ subdir).")
    except subprocess.CalledProcessError:
        print("\nDownload finished (common when gated models need license acceptance).")
        print("Follow the instructions above and re-run.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="foragedj",
        description="Sonic Forage AI DJ — prompt-to-track + real-time mixing + hardware",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    # generate
    p = sub.add_parser("generate", help="Generate a track from a prompt + seed")
    p.add_argument("prompt", help="Text prompt, e.g. 'uplifting trance breakdown 138bpm'")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--duration", type=float, default=60.0)
    p.add_argument("--model", default="small-music", choices=["small-music", "small-sfx", "medium"])
    p.add_argument("--dry", action="store_true", help="Print what would happen without calling the model")
    p.set_defaults(func=cmd_generate)

    # gui
    p = sub.add_parser("gui", help="Launch the Dear PyGui 2-deck interface")
    p.set_defaults(func=cmd_gui)

    # mix
    p = sub.add_parser("mix", help="Mix two pre-generated tracks (placeholder)")
    p.add_argument("deck1")
    p.add_argument("deck2")
    p.add_argument("--crossfade", type=int, default=8, help="Bars")
    p.set_defaults(func=cmd_mix)

    # midi-learn
    p = sub.add_parser("midi-learn", help="Enter MIDI learn mode for a control")
    p.add_argument("--control", default="volume")
    p.set_defaults(func=cmd_midi_learn)

    # doctor (comprehensive self-healing system test)
    p = sub.add_parser("doctor", help="Full system health check with self-healing (--heal to auto-fix issues)")
    p.add_argument("--heal", "--fix", action="store_true", help="Attempt to automatically repair common problems")
    p.set_defaults(func=cmd_doctor)

    # generate-setlist (the "walk away and come back to a full organized library" feature)
    p = sub.add_parser("generate-setlist", help="Generate an entire locked-seed setlist and organize it for harmonic mixing (walk-away mode)")
    p.add_argument("--manifest", required=True, help="Path to setlist manifest (yaml/json)")
    p.add_argument("--dry", action="store_true", help="Dry run (no actual generation, just planning + folder structure)")
    p.set_defaults(func=cmd_generate_setlist)

    # download-models (one-command for core SA3 + all Sonic-Forage LoRAs)
    p = sub.add_parser("download-models", help="Download all core Stable Audio 3 models + Sonic-Forage LoRAs (Z: drive friendly, gated auth guidance)")
    p.set_defaults(func=cmd_download_models)

    # play-library (old-school Winamp vibes for generated sets)
    p = sub.add_parser("play-library", help="Play a generated library folder with crossfades, BPM/key display, and harmonic suggestions (terminal playlist mode)")
    p.add_argument("library_dir", help="Path to a libraries/XXX folder")
    p.add_argument("--auto", action="store_true", help="Auto-play the whole set with smart crossfades")
    p.set_defaults(func=cmd_play_library)

    # live (the big one: autonomous DJ that generates while playing)
    p = sub.add_parser("live", help="Live Autonomous DJ mode — play a setlist while generating the next tracks in the background (lookahead)")
    p.add_argument("--manifest", required=True, help="Path to setlist manifest")
    p.add_argument("--lookahead", type=int, default=2, help="How many tracks to generate ahead (1 or 2 recommended)")
    p.add_argument("--realtime", action="store_true", help="Attempt true realtime generation (only on strong machines)")
    p.set_defaults(func=cmd_live)

    # visualizer (poor man's terminal waveform)
    p = sub.add_parser("visualizer", help="Real-time terminal audio waveform visualizer (great with Resolume or for poor-man's VJing)")
    p.set_defaults(func=cmd_visualizer)

    # osc-resolume (quick start for video sync)
    p = sub.add_parser("osc-resolume", help="Start OSC bridge to Resolume (example for syncing DJ actions to video)")
    p.add_argument("--ip", default="127.0.0.1", help="Resolume IP")
    p.add_argument("--port", type=int, default=7000, help="Resolume OSC port")
    p.set_defaults(func=cmd_osc_resolume)

    # version (explicit)
    p = sub.add_parser("version", help="Print version")
    p.set_defaults(func=cmd_version)

    # os - the full retro operating system interface
    p = sub.add_parser("os", help="Boot the forage-dj Music Diffusion Operating System (retro TUI desktop)")
    p.set_defaults(func=cmd_os)

    # === NEW 2025 ENHANCEMENT + VOICE STACK ===
    p = sub.add_parser("enhance", help="Audio super-resolution & enhancement (FlashSR tiny/fast or AudioSR high-quality)")
    p.add_argument("input", help="Input audio file (wav/mp3 etc.)")
    p.add_argument("--out", help="Output path (default: test_outputs/enhanced/)")
    p.add_argument("--model", default="flashsr-tiny",
                   choices=["flashsr-tiny", "flashsr-onestep", "audiosr"],
                   help="Enhancer to use (flashsr-tiny = instant 200-400x realtime)")
    p.set_defaults(func=cmd_enhance)

    p = sub.add_parser("clean-voice", help="Real-time voice cleaner (LocalVQE: AEC + noise + dereverb on CPU)")
    p.add_argument("mic", help="Mic / vocal recording (16kHz mono ideal)")
    p.add_argument("--ref", help="Optional far-end reference for echo cancellation")
    p.add_argument("--out", help="Output cleaned file")
    p.set_defaults(func=cmd_clean_voice)

    p = sub.add_parser("speak", help="Text-to-speech with Kokoro-82M (lightweight, high quality, many voices)")
    p.add_argument("text", help="Text to speak (use quotes)")
    p.add_argument("--voice", default="af_heart", help="Voice ID (see Kokoro VOICES.md)")
    p.add_argument("--out", help="Output wav path")
    p.set_defaults(func=cmd_speak)

    p = sub.add_parser("split-stems", help="Source separation (Demucs 4-stem etc.) — requires 'stems' extra")
    p.add_argument("input", help="Full mix audio file")
    p.add_argument("--out", help="Output directory for stems")
    p.add_argument("--model", default="htdemucs", help="Demucs model name")
    p.set_defaults(func=cmd_split_stems)

    # === Workstation commands (Ableton-like editing + AI regeneration) ===
    p = sub.add_parser("workstation-new", help="Create a new editable workstation session (like Ableton Live Set)")
    p.add_argument("name", help="Session name")
    p.set_defaults(func=cmd_workstation_new)

    p = sub.add_parser("workstation-add-track", help="Add an audio file as a track in an existing session")
    p.add_argument("session", help="Session name or path to session dir")
    p.add_argument("audio", help="Audio file to add")
    p.set_defaults(func=cmd_workstation_add_track)

    p = sub.add_parser("workstation-regenerate", help="Regenerate a specific region with a new prompt (core workstation superpower)")
    p.add_argument("session", help="Session name or path")
    p.add_argument("track", help="Track id (e.g. track_01)")
    p.add_argument("region", help="Region id (e.g. reg_001)")
    p.add_argument("prompt", help="New prompt for this region")
    p.add_argument("--seed", type=int, default=None)
    p.set_defaults(func=cmd_workstation_regenerate)

    p = sub.add_parser("workstation-view", help="Bad-ass visual arrangement view of a session (terminal Ableton style)")
    p.add_argument("session", help="Session name or path to session dir")
    p.set_defaults(func=cmd_workstation_view)

    p = sub.add_parser("workstation-split", help="Auto-split a track into musical regions using onsets (smart default regions)")
    p.add_argument("session", help="Session name or path")
    p.add_argument("track", help="Track id")
    p.set_defaults(func=cmd_workstation_split)

    # Streaming / Live Performance helper (high priority for real-world use)
    p = sub.add_parser("stream-prep", help="Prepare the workstation for Twitch/Kick/YouTube streaming (clean visuals, OBS tips, latency guidance)")
    p.add_argument("--obs", action="store_true", help="Print OBS scene recommendations")
    p.add_argument("--twitch", action="store_true", help="Print Twitch-specific tips (chat commands, etc.)")
    p.set_defaults(func=cmd_stream_prep)

    p = sub.add_parser("tag-library", help="Make a generated library DJ-app friendly (rename files with BPM+Key, write rich sidecars)")
    p.add_argument("library_dir", help="Path to a libraries/XXX folder")
    p.set_defaults(func=cmd_tag_library)

    # Fun underground rave prep mode (harm reduction culture baked in)
    p = sub.add_parser("rave-prep", help="Underground rave preparation mode — system check + PLUR + harm reduction wisdom")
    p.set_defaults(func=cmd_rave_prep)

    # Swarm Distribution App (autonomous create → organize → analyze → compile → distribute + seed bombing)
    p = sub.add_parser("swarm-distribute", help="Autonomous Swarm Distribution: create/organize/analyze/compile/distribute + seed bomb")
    p.add_argument("--input", required=True, help="Path to session or library")
    p.add_argument("--mode", default="full", choices=["full", "analyze", "compile", "distribute", "seed-bomb"])
    p.add_argument("--seed-bomb", action="store_true", help="Also release generative seeds publicly")
    p.set_defaults(func=cmd_swarm_distribute)

    # Media Player commands (new bad-ass player layer)
    p = sub.add_parser("play-region", help="Play a specific region from a workstation session (media player)")
    p.add_argument("session", help="Session name or path")
    p.add_argument("track", help="Track id (e.g. track_01)")
    p.add_argument("region", help="Region id (e.g. reg_001)")
    p.add_argument("--loop", action="store_true", help="Loop the region")
    p.set_defaults(func=cmd_play_region)

    p = sub.add_parser("player-stop", help="Stop media player playback")
    p.set_defaults(func=cmd_player_stop)

    # AI DJ Personalities (for autonomous sets, chat, promotional characters like "Rex")
    p = sub.add_parser("dj-personalities", help="List or use AI DJ personalities (customizable roleplay scripts)")
    p.add_argument("action", choices=["list", "show", "prompt"], help="list all, show one, or get prompt fragment")
    p.add_argument("name", nargs="?", help="Personality name (e.g. Neon, Vapor, Pulse)")
    p.set_defaults(func=cmd_dj_personalities)

    return parser


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    if hasattr(args, "func"):
        try:
            args.func(args)
        except KeyboardInterrupt:
            print("\nInterrupted.")
            return 130
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        _print_banner()
        # Bad-ass first-boot guided experience
        print("\nFirst time? Run:  uv run foragedj doctor --heal")
        print("Ready to go live? Run: uv run foragedj stream-prep --twitch")
        print("Want the full retro OS? Run: uv run foragedj os")
        parser.print_help()

    return 0


# =============================================================================
# ALL COMMAND HANDLERS (hoisted here so build_parser + `python -m` + health checks work)
# Previously many were defined after the `if __name__` guard — causing NameError on direct execution.
# =============================================================================

def cmd_os(args: argparse.Namespace) -> None:
    """Boot the full retro OS interface."""
    from .os import run_os
    run_os()


# === NEW COMMAND HANDLERS (Enhancement + Voice stack) ===

def cmd_enhance(args: argparse.Namespace) -> None:
    from .enhance import enhance_audio
    out = enhance_audio(args.input, args.out, model=args.model)
    print(f"\n✅ Enhanced audio ready: {out}")
    print("   (For real FlashSR/AudioSR inference see the notes printed above or docs/ENHANCEMENT_TOOLS.md)")


def cmd_clean_voice(args: argparse.Namespace) -> None:
    from .enhance import clean_voice
    out = clean_voice(args.mic, ref_path=args.ref, output_path=args.out)
    print(f"\n✅ Cleaned voice: {out}")
    print("   Real-time LocalVQE binary gives best CPU results — see LocalVQE GitHub + docs.")


def cmd_speak(args: argparse.Namespace) -> None:
    from .enhance import text_to_speech
    out = text_to_speech(args.text, voice=args.voice, output_path=args.out)
    print(f"\n✅ TTS saved: {out}")
    print("   Drop this into libraries/ or play with the mixer / live mode. Great for drops & voiceovers.")


def cmd_split_stems(args: argparse.Namespace) -> None:
    from .enhance import split_stems
    out = split_stems(args.input, output_dir=args.out, model=args.model)
    print(f"\n✅ Stems written under: {out}")
    print("   Use vocals.wav for RVC / further enhancement, drums/bass for remixing.")


# === Workstation (Ableton-style editing, regenerate, inpaint) ===

def cmd_workstation_new(args: argparse.Namespace) -> None:
    from .workstation import create_session
    sess = create_session(args.name)
    sess_dir = sess.save()
    print(f"✅ New workstation session created: {sess.name}")
    print(f"   Location: {sess_dir}")
    print("   Add tracks with: foragedj workstation add-track <session> <audio.wav>")


def cmd_workstation_add_track(args: argparse.Namespace) -> None:
    from .workstation import Session
    sess_dir = Path(args.session)
    if not (sess_dir / "session.json").exists():
        sess_dir = paths.get_sessions_dir() / args.session
    sess = Session.load(sess_dir)
    track = sess.add_track(Path(args.audio))
    sess.save()
    print(f"✅ Added track '{track.name}' to session '{sess.name}'")


def cmd_workstation_regenerate(args: argparse.Namespace) -> None:
    from .workstation import Session, regenerate_region
    sess_dir = Path(args.session)
    if not (sess_dir / "session.json").exists():
        sess_dir = paths.get_sessions_dir() / args.session
    sess = Session.load(sess_dir)
    out = regenerate_region(sess, args.track, args.region, args.prompt, args.seed)
    print(f"✅ Regenerated region → {out}")
    print("   Session updated with new region metadata.")


def cmd_workstation_view(args: argparse.Namespace) -> None:
    from .workstation import Session, render_session_arrangement
    sess_dir = Path(args.session)
    if not (sess_dir / "session.json").exists():
        sess_dir = paths.get_sessions_dir() / args.session
    sess = Session.load(sess_dir)
    render_session_arrangement(sess)


def cmd_workstation_split(args: argparse.Namespace) -> None:
    from .workstation import Session, auto_create_regions_from_onsets
    from . import analysis
    sess_dir = Path(args.session)
    if not (sess_dir / "session.json").exists():
        sess_dir = paths.get_sessions_dir() / args.session
    sess = Session.load(sess_dir)
    track = next((t for t in sess.tracks if t.id == args.track), None)
    if not track:
        print(f"Track {args.track} not found")
        return
    try:
        res = analysis.detect_bpm_key(track.source_path)
        regions = auto_create_regions_from_onsets(track, res)
        sess.save()
        print(f"✅ Auto-split track {args.track} into {len(regions)} musical regions using onsets.")
        print("   Run 'foragedj workstation-view' to see the bad-ass arrangement.")
    except Exception as e:
        print(f"❌ Auto-split failed: {e}")
        print("   Falling back to manual regions or try installing soundfile: uv pip install soundfile")
        # The auto function now has graceful fallback, so try once more
        regions = auto_create_regions_from_onsets(track)
        sess.save()
        print(f"   Created {len(regions)} fallback regions instead.")


def cmd_stream_prep(args: argparse.Namespace) -> None:
    """Help streamers get set up quickly for live performance."""
    print("📺 Sonic Forage — Stream Prep Mode")
    print("=" * 50)
    print("\nRecommended launch for streams:")


# === Remaining referenced handlers (live, visualizer, osc, tag, rave, swarm, player, personalities) ===
# These were previously only defined after the if __name__ guard.

def cmd_live(args: argparse.Namespace) -> None:
    print("🚀 Live Autonomous DJ mode")
    print(f"   Manifest: {args.manifest}")
    print(f"   Lookahead: {args.lookahead}  Realtime: {args.realtime}")
    print("\nReal engine in src/foragedj/mixer.py + audio_gen background generation.")
    print("For now run the full OS (foragedj os) or use generate-setlist + play-library as the walk-away workflow.")
    print("Full lookahead live coming in next agent iteration.")


def cmd_visualizer(args: argparse.Namespace) -> None:
    from .visualizer import run_visualizer
    print("👁️ Launching terminal waveform visualizer...")
    run_visualizer()


def cmd_osc_resolume(args: argparse.Namespace) -> None:
    from .hardware.osc import create_resolume_bridge
    print(f"🌉 Starting OSC Resolume bridge → {args.ip}:{args.port}")
    bridge = create_resolume_bridge(resolume_ip=args.ip, resolume_port=args.port)
    bridge.start()
    print("Bridge running (Ctrl-C to stop). See hardware/osc.py for Resolume mapping examples.")

    print("  uv run foragedj os                 # Boot the retro OS (great visuals)")
    print("  uv run foragedj workstation-view <session>   # Show the arrangement live")
    print("  uv run foragedj live --manifest ... --lookahead 2")
    print("\nFor best terminal capture in OBS:")
    print("  - Use a monospace font, size 18-24pt")
    print("  - Dark theme with high contrast (the default retro green works well)")
    print("  - Capture the whole OS window or specific Rich panels")
    print("  - Consider running in a dedicated tmux pane for the visualizer")

    if args.obs:
        print("\n--- OBS Scene Ideas ---")
        print("Scene 1: 'Retro OS' — full terminal with big fonts")
        print("Scene 2: 'Arrangement View' — workstation-view in a clean pane")
        print("Scene 3: 'Waveform + Chat' — visualizer on left, chat on right")
        print("Scene 4: 'Performance' — mixer status + current prompt big in center")

    if args.twitch:
        print("\n--- Twitch / Kick Tips ---")
        print("• Pin a !prompt command that lets chat suggest the next region prompt")
        print("• Use Nightbot/StreamElements to queue prompts")
        print("• Show the workstation-view during regeneration so viewers see the edit live")
        print("• Title idea: \"Local AI Music Workstation — Chat Controls the Drop\"")

    print("\nPro tip: Run everything after sourcing .grok/hf-cache.env for max speed.")
    print("Quality will keep improving as we add better models and editing features.")
    print("=" * 50)


def cmd_tag_library(args: argparse.Namespace) -> None:
    """Tag an existing library folder so the WAVs are friendly to Serato, Rekordbox, Traktor, Engine DJ, etc."""
    from .utils import tag_wav_for_dj
    import json

    lib_dir = Path(args.library_dir)
    if not lib_dir.exists():
        print(f"Library not found: {lib_dir}")
        return

    print(f"🎛️  Tagging library for DJ apps: {lib_dir}")
    print("   Renaming files to NN_Name_BPM_Key format + writing rich sidecars...")

    json_path = lib_dir / "library.json"
    tracks = {}
    if json_path.exists():
        data = json.loads(json_path.read_text())
        tracks = {t.get("file", ""): t for t in data.get("tracks", [])}

    tagged = 0
    for wav in sorted(lib_dir.glob("*.wav")):
        if wav.stat().st_size == 0:
            print(f"   [skip] {wav.name} (0-byte placeholder)")
            continue

        info = tracks.get(wav.name, {})
        title = info.get("prompt", "")[:60] or wav.stem
        bpm = float(info.get("bpm", 0.0))
        key = info.get("key", "")
        camelot = info.get("camelot", "")

        try:
            new_path = tag_wav_for_dj(wav, title=title, bpm=bpm, key=key, camelot=camelot,
                                      comment=info.get("prompt", ""))
            print(f"   ✓ {wav.name} → {new_path.name}")
            tagged += 1
        except Exception as e:
            print(f"   ✗ {wav.name}: {e}")

    print(f"\n✅ Tagged {tagged} tracks.")
    print("   Load the folder in your DJ software — you should now see BPM + Key in the filenames.")


def cmd_rave_prep(args: argparse.Namespace) -> None:
    """Underground rave preparation experience.
    Runs the main system test (doctor) with harm reduction flavor,
    PLUR reminders, and practical prep advice for throwing or attending proper events.
    """
    from .health import run_full_health_check

    print("\n" + "=" * 60)
    print("🌊  UNDERGROUND RAVE PREP MODE  🌊")
    print("=" * 60)
    print()
    print("Before we check the machines, a reminder from the culture:")
    print()
    print("   P.L.U.R.  —  Peace  •  Love  •  Unity  •  Respect")
    print()
    print("This is why we build tools like this.")
    print("This is why we give the music away at events.")
    print("This is why we pass out water and donuts instead of just vibes.")
    print()

    # Run the actual main test (doctor) with heal
    print("Running full system check with rave eyes...\n")
    run_full_health_check(fix=True)

    print("\n" + "-" * 60)
    print("Practical Underground Prep Advice:")
    print("-" * 60)
    print("""
• Drink water. Seriously. Set a timer if you have to.
• Eat something before you go deep.
• Look after your friends — and the strangers next to you.
• If you're throwing the event: have a chill space, free water, and harm reduction info visible.
• Test your rig *before* doors. Don't be the person debugging at 2am.
• PLUR isn't just a slogan when the lights are off and the bass is heavy. It's the operating system.

The machines are ready when you are.

Now go make something beautiful, safe, and slightly illegal in spirit (even if it's fully permitted).
""")
    print("=" * 60)
    print("Stay hydrated. Stay kind. Keep the underground alive.\n")


def cmd_swarm_distribute(args: argparse.Namespace) -> None:
    """Entry point for the autonomous Swarm Distribution App."""
    import subprocess
    cmd = [
        "uv", "run", "python", "scripts/swarm_distributor.py",
        "--input", args.input,
        "--mode", args.mode
    ]
    if args.seed_bomb:
        cmd.append("--seed-bomb")

    print("🚀 Launching Swarm Distribution App...")
    subprocess.run(cmd)


def cmd_play_region(args: argparse.Namespace) -> None:
    """Play a specific region using the new media player."""
    from .player import media_player
    from .workstation import Session

    sess_dir = Path(args.session)
    if not (sess_dir / "session.json").exists():
        sess_dir = paths.get_sessions_dir() / args.session

    session = Session.load(sess_dir)
    media_player.load_session(session)
    media_player.play_region(args.track, args.region, loop=args.loop)
    print(f"▶️  Playing region {args.region} from {args.track} (loop={args.loop})")
    print("   Use 'foragedj player-stop' to stop.")


def cmd_player_stop(args: argparse.Namespace) -> None:
    """Stop the media player."""
    from .player import media_player
    media_player.stop()
    print("⏹️  Media player stopped.")


def cmd_dj_personalities(args: argparse.Namespace) -> None:
    """Interact with AI DJ personalities."""
    from .personalities import load_personalities, get_personality, list_personalities

    if args.action == "list":
        print("Available AI DJ Personalities:")
        for name in list_personalities():
            print(f"  • {name}")
        print("\nUse: foragedj dj-personalities show <name>")
        print("Use: foragedj dj-personalities prompt <name>   (for AI system prompts)")

    elif args.action == "show":
        if not args.name:
            print("Please provide a personality name.")
            return
        p = get_personality(args.name)
        if not p:
            print(f"Personality '{args.name}' not found.")
            return
        print(f"\n{p.dj_name}")
        print(f"Vibe: {p.vibe}")
        print(f"Loves: {', '.join(p.favorite_styles)}")
        print(f"Dislikes: {', '.join(p.disliked_styles)}")
        print(f"Personality: {p.personality}")
        print(f"Catchphrases: {' | '.join(p.catchphrases)}")

    elif args.action == "prompt":
        if not args.name:
            print("Please provide a personality name.")
            return
        p = get_personality(args.name)
        if not p:
            print(f"Personality '{args.name}' not found.")
            return
        print(p.get_prompt_fragment())


# (All command handlers are now hoisted above build_parser for correct module load order.
# This fixes `python -m foragedj.cli` and the health.py doctor check.)
