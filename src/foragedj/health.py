"""
Self-healing system health checker for forage-dj.

Usage:
    uv run foragedj doctor --heal
    uv run foragedj health --fix

It checks every major subsystem and attempts to automatically repair common issues.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .config import CONFIG_DIR, CONFIG_PATH, load_config
from .paths import (
    PROJECT_ROOT,
    get_checkpoints_dir,
    get_data_root,
    get_generated_dir,
    get_hf_home,
    get_sessions_dir,
    ensure_data_dirs,
    write_paths_json,
)

console = Console()

CHECKPOINTS_DIR = get_checkpoints_dir()
ENHANCERS_DIR = CHECKPOINTS_DIR / "enhancers"
VOICE_DIR = CHECKPOINTS_DIR / "voice"
SETLISTS_DIR = PROJECT_ROOT / "setlists"
LIBRARIES_DIR = get_data_root() / "libraries"

REQUIRED_DIRS = [
    PROJECT_ROOT / ".grok",
    CHECKPOINTS_DIR,
    ENHANCERS_DIR,
    VOICE_DIR,
    SETLISTS_DIR,
    LIBRARIES_DIR,
    get_generated_dir(),
    get_sessions_dir(),
    PROJECT_ROOT / "test_outputs",
]

class HealthReport:
    def __init__(self):
        self.checks: List[Dict[str, Any]] = []
        self.fixes_applied: List[str] = []
        self.critical_issues: List[str] = []

    def add_check(self, name: str, status: str, message: str = "", fixable: bool = False):
        self.checks.append({
            "name": name,
            "status": status,  # "ok", "warning", "error"
            "message": message,
            "fixable": fixable
        })

    def add_fix(self, description: str):
        self.fixes_applied.append(description)

    def add_critical(self, message: str):
        self.critical_issues.append(message)

    def has_errors(self) -> bool:
        return any(c["status"] == "error" for c in self.checks)

    def print_report(self):
        console.print("\n[bold]🍓 forage-dj Health Report[/bold]\n")

        for check in self.checks:
            color = {
                "ok": "green",
                "warning": "yellow",
                "error": "red"
            }.get(check["status"], "white")

            icon = "✅" if check["status"] == "ok" else "⚠️" if check["status"] == "warning" else "❌"
            console.print(f"{icon} [{color}]{check['name']}[/{color}]: {check['message']}")

        if self.fixes_applied:
            console.print("\n[bold green]Fixes Applied:[/bold green]")
            for fix in self.fixes_applied:
                console.print(f"  • {fix}")

        if self.critical_issues:
            console.print("\n[bold red]Critical Issues Remaining:[/bold red]")
            for issue in self.critical_issues:
                console.print(f"  • {issue}")


def check_environment(report: HealthReport):
    """Check Python, uv, venv location, etc."""
    # Python version
    if sys.version_info < (3, 12):
        report.add_check("Python Version", "error", f"Python {sys.version_info} < 3.12 required", fixable=False)
    else:
        report.add_check("Python Version", "ok", f"Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check if running from project .venv
    venv_path = Path(sys.prefix)
    if "forage-dj" not in str(venv_path) and ".venv" not in str(venv_path):
        report.add_check("Virtual Environment", "warning", "Not running from project .venv (recommended for large audio work)")
    else:
        report.add_check("Virtual Environment", "ok", f"Using {venv_path}")

    # uv available?
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        report.add_check("uv Package Manager", "ok", "uv is available")
    except Exception:
        report.add_check("uv Package Manager", "error", "uv not found in PATH", fixable=True)


def check_paths(report: HealthReport):
    """Ensure all critical directories exist (respects large storage root on any OS)."""
    for path in REQUIRED_DIRS:
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                report.add_fix(f"Created missing directory: {path}")
                report.add_check(f"Directory: {path.name}", "ok", "Created")
            except Exception as e:
                report.add_check(f"Directory: {path.name}", "error", str(e))
        else:
            report.add_check(f"Directory: {path.name}", "ok", "Present")


def check_config(report: HealthReport):
    """Check and repair config."""
    try:
        cfg = load_config()
        report.add_check("Configuration", "ok", "Config loaded successfully")
    except Exception as e:
        report.add_check("Configuration", "warning", f"Config issue: {e}", fixable=True)
        # Attempt repair
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump({"live": {"default_lookahead": 2}}, f, indent=2)
            report.add_fix("Recreated default config.json")
        except Exception as fix_e:
            report.add_critical(f"Failed to repair config: {fix_e}")


def check_models(report: HealthReport):
    """Check if any models/LoRAs are present."""
    if not CHECKPOINTS_DIR.exists():
        report.add_check("Models / Checkpoints", "warning", "checkpoints/ directory missing")
        return

    core_models = list(CHECKPOINTS_DIR.glob("stable-audio-3-*"))
    loras = list((CHECKPOINTS_DIR / "loras").glob("*")) if (CHECKPOINTS_DIR / "loras").exists() else []
    enhancers = list(ENHANCERS_DIR.glob("*")) if ENHANCERS_DIR.exists() else []
    voice = list(VOICE_DIR.glob("*")) if VOICE_DIR.exists() else []

    if core_models or loras or enhancers or voice:
        msg = f"Core: {len(core_models)} | LoRAs: {len(loras)} | Enhancers: {len(enhancers)} | Voice: {len(voice)}"
        report.add_check("Models / Checkpoints", "ok", msg)
    else:
        report.add_check("Models / Checkpoints", "warning", "No models downloaded yet. Run 'foragedj download-models'", fixable=True)


def check_cli(report: HealthReport):
    """Verify all expected CLI commands are registered."""
    expected = ["generate", "generate-setlist", "live", "download-models", "play-library", "doctor",
                "enhance", "clean-voice", "speak", "split-stems",
                "workstation-new", "workstation-add-track", "workstation-regenerate"]
    try:
        result = subprocess.run(
            [sys.executable, "-m", "foragedj.cli", "--help"],
            capture_output=True, text=True, timeout=10
        )
        help_text = result.stdout + result.stderr
        missing = [cmd for cmd in expected if cmd not in help_text]
        if missing:
            report.add_check("CLI Commands", "warning", f"Missing commands: {missing}")
        else:
            report.add_check("CLI Commands", "ok", "All core commands present")
    except Exception as e:
        report.add_check("CLI Commands", "error", str(e))


def check_hf_auth(report: HealthReport):
    """Check Hugging Face authentication and gated model situation."""
    token = os.environ.get("HF_TOKEN")
    cache_env = PROJECT_ROOT / ".grok/hf-cache.env"
    token_env = PROJECT_ROOT / ".grok/hf-token.env"

    if token:
        report.add_check("HF Authentication", "ok", "HF_TOKEN detected in environment (good for rate limits)")
    else:
        report.add_check("HF Authentication", "warning",
                         "No HF_TOKEN set — downloads will be slow/unauthenticated", fixable=True)

    if not cache_env.exists():
        report.add_check("HF Cache Config", "warning", ".grok/hf-cache.env (or .ps1) missing", fixable=True)
    else:
        report.add_check("HF Cache Config", "ok", "HF cache config present (cross-platform)")

    if token_env.exists():
        report.add_check("HF Token File", "ok", "Local token file exists (.grok/hf-token.env)")
    else:
        report.add_check("HF Token File", "warning", "No .grok/hf-token.env (recommended for convenience)", fixable=True)


def check_models_detailed(report: HealthReport):
    """Detailed check of downloaded models, LoRAs, enhancers, and voice tools."""
    if not CHECKPOINTS_DIR.exists():
        report.add_check("Models & Tools", "warning", "checkpoints/ directory does not exist")
        return

    # Core models
    core = {
        "small-music": (CHECKPOINTS_DIR / "stable-audio-3-small-music").exists(),
        "small-sfx": (CHECKPOINTS_DIR / "stable-audio-3-small-sfx").exists(),
        "medium": (CHECKPOINTS_DIR / "stable-audio-3-medium").exists(),
        "optimized": (CHECKPOINTS_DIR / "stable-audio-3-optimized").exists(),
    }

    # Autoencoders
    same = {
        "SAME-S": (CHECKPOINTS_DIR / "SAME-S").exists(),
        "SAME-L": (CHECKPOINTS_DIR / "SAME-L").exists(),
    }

    # Sonic-Forage LoRAs
    lora_dir = CHECKPOINTS_DIR / "loras"
    sonic_loras = list(lora_dir.glob("*")) if lora_dir.exists() else []

    # New 2025 enhancement + voice stack
    flash_tiny = (ENHANCERS_DIR / "flashsr-tiny").exists()
    flash_onestep = (ENHANCERS_DIR / "flashsr-onestep").exists()
    audiosr = (ENHANCERS_DIR / "audiosr").exists()
    localvqe = (VOICE_DIR / "localvqe").exists() or any((VOICE_DIR).glob("*.gguf"))

    present_core = [k for k, v in core.items() if v]
    present_same = [k for k, v in same.items() if v]

    enhancer_count = sum([flash_tiny, flash_onestep, audiosr])
    voice_count = 1 if localvqe else 0

    sessions_dir = get_sessions_dir()
    generated_dir = get_generated_dir()
    has_sessions = sessions_dir.exists() and any(sessions_dir.iterdir())
    has_generated = generated_dir.exists() and any(generated_dir.iterdir())

    if present_core or present_same or sonic_loras or enhancer_count or voice_count or has_sessions or has_generated:
        msg = (f"Core: {len(present_core)}/4 | LoRAs: {len(sonic_loras)} | "
               f"Enhancers: {enhancer_count}/3 | Voice: {voice_count} | "
               f"Sessions: {'yes' if has_sessions else 'no'} | Generated: {'yes' if has_generated else 'no'}")
        report.add_check("Models & Workstation (sessions + generated)", "ok", msg)
    else:
        report.add_check("Models & Tools (incl. new enhancers + voice)", "warning",
                         "Run 'foragedj download-models --group all' (see docs for new AudioSR/FlashSR/LocalVQE/Kokoro)")


def check_core_modules(report: HealthReport):
    """Test that critical modules can be imported and have basic functionality."""
    modules_to_test = [
        ("foragedj.config", "config system"),
        ("foragedj.analysis", "BPM/Key analysis"),
        ("foragedj.setlist", "setlist manifest system"),
        ("foragedj.mixer", "realtime mixer"),
    ]

    for mod, desc in modules_to_test:
        try:
            __import__(mod)
            report.add_check(f"Module: {desc}", "ok", "Imports successfully")
        except Exception as e:
            report.add_check(f"Module: {desc}", "error", f"Import failed: {e}", fixable=True)


def check_setlist_system(report: HealthReport):
    """Validate that setlist manifests exist and are loadable."""
    if not SETLISTS_DIR.exists():
        report.add_check("Setlist System", "warning", "setlists/ directory missing")
        return

    manifests = list(SETLISTS_DIR.glob("*.yaml")) + list(SETLISTS_DIR.glob("*.yml"))
    if manifests:
        report.add_check("Setlist System", "ok", f"{len(manifests)} manifest(s) found")
    else:
        report.add_check("Setlist System", "warning", "No setlist manifests found (run generation first?)")


def check_live_readiness(report: HealthReport):
    """Check if the system is ready for live autonomous DJ mode."""
    # This is a higher-level check
    has_manifests = len(list(SETLISTS_DIR.glob("*.yaml"))) > 0 if SETLISTS_DIR.exists() else False
    has_config = CONFIG_PATH.exists()

    if has_manifests and has_config:
        report.add_check("Live Autonomous DJ", "ok", "Ready for 'foragedj live' (manifests + config present)")
    else:
        report.add_check("Live Autonomous DJ", "warning",
                         "Missing manifests or config — 'live' mode not fully ready yet", fixable=True)


def self_heal(report: HealthReport):
    """Attempt to automatically fix common problems."""
    fixes = []

    # 1. Create missing critical directories (including new enhancers/ + voice/ for 2025 stack)
    for path in REQUIRED_DIRS:
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                fixes.append(f"Created directory: {path.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                report.add_critical(f"Could not create {path}: {e}")

    # 2. Create default HF token template if missing
    token_template = PROJECT_ROOT / ".grok/hf-token.env"
    if not token_template.exists():
        try:
            token_template.write_text(
                "# Put your Hugging Face token here (never commit this file!)\n"
                "# export HF_TOKEN=hf_your_token_here\n"
            )
            token_template.chmod(0o600)
            fixes.append("Created .grok/hf-token.env template (edit it with your token)")
        except Exception as e:
            report.add_critical(f"Could not create token template: {e}")

    # 3. Create default cross-platform HF cache helper + paths.json
    cache_env = PROJECT_ROOT / ".grok/hf-cache.env"
    if not cache_env.exists():
        try:
            from .paths import get_env_activation_hints, get_hf_home, write_paths_json
            hf = get_hf_home()
            hints = get_env_activation_hints()
            cache_env.write_text(
                f"# Cross-platform HF cache (generated by doctor)\n"
                f"# Linux/mac:  source .grok/hf-cache.env\n"
                f"# Windows:    . .grok/hf-cache.ps1   (PowerShell)\n\n"
                f"export HF_HOME={hf}\n"
                f"export HUGGINGFACE_HUB_CACHE=$HF_HOME/hub\n\n"
                f"# PowerShell equivalent:\n"
                f"# $env:HF_HOME = '{hf}'\n"
                f"# $env:HUGGINGFACE_HUB_CACHE = '{hf}/hub'\n"
            )
            # Also write a .ps1 helper
            ps1 = PROJECT_ROOT / ".grok/hf-cache.ps1"
            ps1.write_text(hints["powershell"] + "\nWrite-Host \"HF cache set to: $env:HF_HOME\"")
            write_paths_json()
            fixes.append("Created .grok/hf-cache.env + .ps1 (cross-platform HF cache)")
        except Exception as e:
            report.add_critical(f"Could not create cache env helpers: {e}")

    # 4. Create basic config if missing
    if not CONFIG_PATH.exists():
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps({"live": {"default_lookahead": 2}}, indent=2))
            fixes.append("Created default config.json")
        except Exception as e:
            report.add_critical(f"Could not create config: {e}")

    for fix in fixes:
        report.add_fix(fix)


def run_full_health_check(fix: bool = False) -> HealthReport:
    report = HealthReport()

    console.print("[bold]🍓 Running forage-dj Comprehensive Self-Healing Health Check...[/bold]\n")

    check_environment(report)
    check_paths(report)
    check_config(report)
    check_hf_auth(report)
    check_models_detailed(report)
    check_core_modules(report)
    check_setlist_system(report)
    check_live_readiness(report)
    check_cli(report)

    if fix:
        self_heal(report)

    report.print_report()

    if report.has_errors():
        console.print("\n[red]Some issues remain. Many were auto-fixed above.[/red]")
        console.print("Run again with --heal if you want to attempt more repairs.")
    else:
        console.print("\n[bold green]✅ All systems look healthy (or were successfully repaired).[/bold green]")

    return report
