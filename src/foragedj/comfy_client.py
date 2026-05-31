"""
ComfyUI client for ForageDJ.

This lets the rest of the app (generate_track, CLI, setlist, workstation)
treat ComfyUI as a reliable backend for heavy audio models (especially
stable-audio-open-1.0 and your optimized SA3 checkpoints).

Usage with your server running at http://0.0.0.0:8188:

    from src.foragedj.comfy_client import generate_via_comfy

    wav_path = generate_via_comfy(
        prompt="dark rolling techno 128bpm",
        seed=424242,
        duration=12,
        workflow_path="workflows/comfy/stable-audio-open.json",
        # comfy_url defaults to http://127.0.0.1:8188 which works great
        # when your server is bound to 0.0.0.0:8188 on this machine
    )

Or set the environment variable:
    export COMFYUI_URL=http://127.0.0.1:8188

The client uses ComfyUI's native /prompt + /history API.
It returns the path to the generated WAV.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Optional

import httpx

from .paths import get_comfy_output_dir, get_comfy_workflows_dir


def _resolve_comfy_url(url: str | None) -> str:
    """Choose a sensible default URL for a ComfyUI server bound to 0.0.0.0:8188."""
    if url:
        u = url.rstrip("/")
        # 0.0.0.0 is a bind address, not a connectable destination. Normalize it.
        if "0.0.0.0" in u:
            u = u.replace("0.0.0.0", "127.0.0.1")
        return u
    env = os.environ.get("COMFYUI_URL")
    if env:
        u = env.rstrip("/")
        if "0.0.0.0" in u:
            u = u.replace("0.0.0.0", "127.0.0.1")
        return u
    # 127.0.0.1 is the most reliable client address even when server listens on 0.0.0.0
    return "http://127.0.0.1:8188"


def _get_possible_output_dirs() -> list[Path]:
    """Return candidate directories (in priority order) where ComfyUI may have written the file."""
    dirs: list[Path] = []

    # 1. Explicit env var (highest priority)
    if env := os.environ.get("COMFYUI_OUTPUT_DIR"):
        dirs.append(Path(env).expanduser().resolve())

    # 2. The project's managed location
    try:
        dirs.append(get_comfy_output_dir())
    except Exception:
        pass

    # 3. Common native ComfyUI locations (relative to CWD or home)
    cwd = Path.cwd()
    dirs.extend([
        cwd / "comfyui_output",
        cwd / "output",
        cwd / "ComfyUI" / "output",
        Path.home() / "ComfyUI" / "output",
        Path("/comfyui/output"),  # inside the project's docker container
    ])

    # 4. The old hardcoded Z: location as last-ditch fallback
    dirs.append(Path("/mnt/z/IMF2045/forage-dj/comfyui_output"))

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for d in dirs:
        try:
            rp = d.resolve()
        except Exception:
            rp = d
        if rp not in seen:
            seen.add(rp)
            unique.append(d)
    return unique


def _find_output_file(filename: str) -> Path | None:
    """Search all likely output directories for the generated file."""
    if not filename:
        return None
    fname = Path(filename).name  # be defensive
    for base in _get_possible_output_dirs():
        candidate = base / fname
        if candidate.exists():
            return candidate
        # Some workflows save into subfolders
        for sub in base.rglob(fname):
            if sub.is_file():
                return sub
    return None


def generate_via_comfy(
    prompt: str,
    seed: int = 42,
    duration: float = 12.0,
    workflow_path: str | Path = "workflows/comfy/stable-audio-open.json",
    comfy_url: str | None = None,
    timeout: int = 300,
    poll_interval: float = 1.0,
) -> Path:
    """
    Queue a generation job on a running ComfyUI server and wait for the WAV.

    Works with a ComfyUI server running anywhere (including one bound to
    http://0.0.0.0:8188 on this machine — we connect via 127.0.0.1).

    Expects your workflow to expose these inputs (via "Primitive" or "String"
    nodes with titles exactly like this):
        - "prompt"
        - "seed" (int)
        - "duration" (float, in seconds)

    The workflow should end with a SaveAudio node.
    """
    url = _resolve_comfy_url(comfy_url)

    # Resolve workflow relative to known comfy workflows dir if not absolute
    wp = Path(workflow_path)
    if not wp.is_absolute():
        candidate = get_comfy_workflows_dir() / wp.name
        if candidate.exists():
            wp = candidate
        else:
            wp = Path.cwd() / wp
    if not wp.exists():
        raise FileNotFoundError(f"ComfyUI workflow not found: {wp}")

    with open(wp) as f:
        workflow = json.load(f)

    # Inject the runtime values into the workflow
    # This assumes you named the input nodes with titles "prompt", "seed", "duration"
    for node in workflow.values():
        if node.get("title") == "prompt":
            node["inputs"]["text"] = prompt
        elif node.get("title") == "seed":
            node["inputs"]["value"] = int(seed)
        elif node.get("title") == "duration":
            node["inputs"]["value"] = float(duration)

    client_id = str(uuid.uuid4())

    with httpx.Client(timeout=30.0) as client:
        # Queue the prompt
        resp = client.post(
            f"{url}/prompt",
            json={"prompt": workflow, "client_id": client_id},
        )
        resp.raise_for_status()
        prompt_id = resp.json()["prompt_id"]

        # Poll for completion
        start = time.time()
        while time.time() - start < timeout:
            hist = client.get(f"{url}/history/{prompt_id}").json()
            if prompt_id in hist:
                status = hist[prompt_id].get("status", {})
                if status.get("completed"):
                    outputs = hist[prompt_id].get("outputs", {})
                    for node_id, node_out in outputs.items():
                        if "audio" in node_out:
                            audio_info = node_out["audio"][0]
                            filename = audio_info.get("filename") or audio_info.get("name")
                            if filename:
                                found = _find_output_file(filename)
                                if found:
                                    return found
                                # Last resort: return the name and let caller deal with it
                                return Path(filename)
                    raise RuntimeError("ComfyUI finished but no audio output found in history")
                if status.get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI error: {hist[prompt_id]}")
            time.sleep(poll_interval)

        raise TimeoutError(f"ComfyUI generation timed out after {timeout}s (prompt_id={prompt_id})")


def test_comfy_connection(comfy_url: str | None = None) -> dict:
    """
    Quick health check against your running ComfyUI server.

    Example:
        from src.foragedj.comfy_client import test_comfy_connection
        print(test_comfy_connection("http://127.0.0.1:8188"))
    """
    url = _resolve_comfy_url(comfy_url)
    try:
        with httpx.Client(timeout=8.0) as client:
            r = client.get(f"{url}/system_stats")
            r.raise_for_status()
            stats = r.json()
            return {
                "ok": True,
                "url": url,
                "status": "connected",
                "system": stats,
            }
    except Exception as e:
        return {"ok": False, "url": url, "status": "error", "error": str(e)}


# Convenience wrapper so you can call it similarly to the current generate_track
def comfy_generate(
    prompt: str,
    seed: int = 42,
    duration: float = 12.0,
    model: str = "open",  # "open" or "medium" once you have workflows for both
    **kwargs,
) -> Path:
    workflow = f"stable-audio-{model}.json"
    # generate_via_comfy will resolve against get_comfy_workflows_dir()
    return generate_via_comfy(
        prompt=prompt,
        seed=seed,
        duration=duration,
        workflow_path=workflow,
        **kwargs,
    )


def run_comfy_workflow(
    workflow: dict,
    overrides: dict | None = None,
    comfy_url: str | None = None,
    timeout: int = 300,
    poll_interval: float = 2.0,
) -> dict:
    """
    General-purpose runner for arbitrary ComfyUI API-format workflows.

    This is the recommended path for complex audio workflows (e.g. your ACE-Step 1.5 XL Turbo blueprint).

    Args:
        workflow: Already-loaded API-format workflow dict.
        overrides: Dict of {node_id: {input_key: value, ...}} to apply before queuing.
        comfy_url: Target ComfyUI server (respects COMFYUI_URL env var).
        timeout: Max seconds to wait.

    Returns the final history entry for the prompt (contains outputs).
    """
    url = _resolve_comfy_url(comfy_url)
    wf = json.loads(json.dumps(workflow))  # deep copy

    if overrides:
        for node_id, changes in overrides.items():
            if node_id in wf:
                wf[node_id].setdefault("inputs", {}).update(changes)

    client_id = str(uuid.uuid4())

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(f"{url}/prompt", json={"prompt": wf, "client_id": client_id})
        resp.raise_for_status()
        prompt_id = resp.json()["prompt_id"]

        start = time.time()
        while time.time() - start < timeout:
            hist = client.get(f"{url}/history/{prompt_id}").json()
            if prompt_id in hist:
                status = hist[prompt_id].get("status", {})
                if status.get("completed"):
                    return hist[prompt_id]
                if status.get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI error: {hist[prompt_id]}")
            time.sleep(poll_interval)

        raise TimeoutError(f"ComfyUI generation timed out (prompt_id={prompt_id})")