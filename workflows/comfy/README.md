# ComfyUI Workflows for ForageDJ

This directory holds version-controlled ComfyUI workflows used by ForageDJ for audio generation.

## How to use with your running ComfyUI server

Your ComfyUI is running at `http://0.0.0.0:8188` (accessible locally via `http://127.0.0.1:8188` or `http://localhost:8188`).

### Recommended workflow

1. Open your ComfyUI at http://127.0.0.1:8188 (or the address you use)

2. Load one of the workflows from this folder (or build one)

3. **Important**: Add three input nodes with **exact titles** (use the Title field on the node):
   - A node titled exactly `prompt` (String or Primitive → string)
   - A node titled exactly `seed` (Int or Primitive → int)
   - A node titled exactly `duration` (Float or Primitive → float, in seconds)

4. Add a SaveAudio (or Save Audio) node at the end so outputs are written to disk.

5. **Save the workflow** as JSON:
   - In ComfyUI: Menu → Save → save as e.g. `stable-audio-open.json`
   - Copy the `.json` file into this `workflows/comfy/` directory

6. ForageDJ will pick it up automatically when you use `--backend comfy` or set `backend="comfy"`

### Calling from code / CLI

```bash
# Using env var to point at your server (0.0.0.0 binding is fine on the server side)
COMFYUI_URL=http://127.0.0.1:8188 \
  uv run foragedj generate "dark rolling techno 128bpm" --backend comfy --duration 12
```

Or in Python:

```python
from src.foragedj.comfy_client import generate_via_comfy

wav = generate_via_comfy(
    prompt="energetic bass house drop",
    seed=424242,
    duration=30,
    workflow_path="workflows/comfy/stable-audio-open.json",
    comfy_url="http://127.0.0.1:8188",   # or omit to use COMFYUI_URL env / default
)
```

### Environment variables

- `COMFYUI_URL` — Full URL to your ComfyUI (default: http://127.0.0.1:8188)
- `COMFYUI_OUTPUT_DIR` — Where your ComfyUI actually writes generated files (optional, auto-detected in many cases)

### Workflow naming convention

- `stable-audio-open.json` — for stability-ai/stable-audio-open-1.0
- `<model>.json` — e.g. `medium.json`, `sa3-medium-trt.json` for other models
- Keep them in this folder so they are git-tracked and portable

### Docker ComfyUI (alternative)

If you prefer running ComfyUI in the project's Docker container instead of natively:

```bash
./scripts/launch_comfyui.sh
```

This mounts `checkpoints/` and `comfyui_output/`. You can also load workflows from this folder after copying them in.

## Current workflows

- `stable-audio-open.json` — Example for Stable Audio Open 1.0 (update with your nodes + input titles)

## Tips for reliable workflows

- Use the exact node titles `prompt`, `seed`, `duration` (case-sensitive).
- Make sure the last node is a SaveAudio that writes `.wav`.
- For optimized checkpoints (TensorRT/ONNX), install the matching custom nodes via ComfyUI-Manager.
- Test generation manually in the UI first before calling from ForageDJ.

When everything is wired, you get rock-solid local generation without Python dependency hell.
