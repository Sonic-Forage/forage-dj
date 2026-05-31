# ComfyUI Setup for ForageDJ (Recommended Path)

This is the current recommended way to run reliable generation, especially for the heavy models (stable-audio-open and your local medium checkpoint with optimized variants).

## Why ComfyUI?

- Much more stable than the pure Python `stable-audio-3` path (avoids T5Gemma import fights, device leaks, flash-attn + torchvision conflicts).
- Can directly use your optimized checkpoints in `checkpoints/stable-audio-3-optimized/` (TensorRT, ONNX, etc.).
- Visual workflows make debugging and iteration much easier.
- ForageDJ can call it as a backend service via HTTP.

## Quick Start

1. Make sure Docker + NVIDIA Container Toolkit is working on your system.

2. Launch ComfyUI (pick one):

   **Option A — Native (recommended for you right now)**  
   Run your existing ComfyUI install and make sure it is listening on `0.0.0.0:8188`.

   **Option B — Project Docker container**  
   ```bash
   ./scripts/launch_comfyui.sh
   ```

3. Open http://127.0.0.1:8188 (or http://localhost:8188)

4. Install custom nodes (via ComfyUI-Manager):
   - Search for "Stable Audio Open" or "StableAudio"
   - Install any TensorRT / ONNX nodes if you want to use the optimized versions

5. Create or load a workflow for `stable-audio-open-1.0` (or medium once nodes support it better).

6. Save useful workflows to `workflows/comfy/`.

## Calling from ForageDJ

```python
from src.foragedj.comfy_client import generate_via_comfy

# Works great with your server running on http://0.0.0.0:8188
wav = generate_via_comfy(
    prompt="dark rolling techno 128bpm",
    seed=424242,
    duration=12,
    workflow_path="workflows/comfy/stable-audio-open.json",
    # comfy_url omitted → uses COMFYUI_URL env or http://127.0.0.1:8188
)
```

## Volumes & Paths

The Docker service mounts:
- Your full `checkpoints/` folder (read-only)
- `comfyui_output/` for generated files
- `workflows/comfy/` → inside the container so you can load/save versioned workflows directly from the UI

This keeps everything on your Z: drive.

When running ComfyUI **natively** (your current setup at 0.0.0.0:8188), just save your workflows into the `workflows/comfy/` folder in this project. ForageDJ will find them automatically.

## Quick test from your running server

```python
from src.foragedj.comfy_client import test_comfy_connection
print(test_comfy_connection())   # should say "connected" if your server on 8188 is reachable
```

## Next Improvements (planned)

- Thin FastAPI wrapper around ComfyUI for a friendlier `/generate` endpoint
- CLI flag: `foragedj generate "..." --backend comfy`
- Automatic workflow selection based on model

---

This approach should finally give you something that "just works" without the constant Python environment rot.