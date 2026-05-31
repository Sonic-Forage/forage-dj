# Working with Remote (and Local) ComfyUI Servers

## The Core Principle

ForageDJ itself does **not** need to run the heavy models. It only needs to talk to a ComfyUI server (via HTTP) and handle the results.

This means the ComfyUI server can be:
- On the user's Windows machine (accessed via Tailscale)
- On a remote GPU pod (RunPod, Vast.ai, TensorDock, etc.)
- On another computer entirely
- Even a shared team server

## Recommended Configuration Pattern

Use the existing config system:

```python
from src.foragedj.config import set_default_backend
set_default_backend("comfy", "http://YOUR-SERVER-IP:8188")
```

Or set the environment variable:
```bash
export COMFYUI_URL=http://YOUR-SERVER-IP:8188
```

## Common Setups

### Local Windows Machine (via Tailscale)
- URL: `http://100.99.10.17:8188` (or whatever the Windows Tailscale IP is)
- Usually the most convenient for the user

### Remote RunPod / Vast.ai Pod
- Get the public IP + port from the pod dashboard
- Make sure ComfyUI was started with `--listen 0.0.0.0 --port 8188`
- Optionally set up a simple reverse proxy or use the pod's built-in networking
- Be careful with long-running generations (pods can have timeouts or get shut down)

### Hybrid
- User does quick tests locally
- Switches to a powerful remote pod for longer or higher-quality generations

## Things to Watch For With Remote Servers

- Output files are written on the remote machine. You need a strategy to get them back (download via API, shared storage, explicit upload step in the workflow, etc.).
- Timeouts — long audio generations can take minutes. Set generous timeouts in the client.
- Authentication — most pods don't require it, but some custom setups might.
- Model availability — the exact models and custom nodes the workflow needs must be present on the remote server.

## Future Nice-to-Haves

- Named server profiles in config (`local`, `runpod-big-gpu`, `team-server`, etc.)
- Automatic result downloading / uploading
- Queue management and status for remote servers
- Cost-aware scheduling (cheap small pod vs expensive big pod)

For now, keep it simple: one active `COMFYUI_URL` at a time, easy to change.
