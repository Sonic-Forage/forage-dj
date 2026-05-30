---
name: forage-dj-on-runpod
description: Deploy and manage the forage-dj Music Diffusion Operating System on RunPod GPU cloud. Includes templates, network volumes for large models, the retro OS interface, live autonomous DJ mode, and agentic tools.
allowed-tools: Bash(runpodctl:*), Bash(python:*), ReadFile, WriteFile
compatibility: Linux, macOS
metadata:
  author: Sonic-Forage
  version: "0.1.0"
  project: https://github.com/Sonic-Forage/forage-dj
license: MIT
---

# forage-dj on RunPod

**forage-dj** is the first Music Diffusion Operating System — an autonomous, agentic, terminal-first AI DJ workstation powered by Stable Audio 3 + community LoRAs.

This skill teaches you how to deploy the full experience on RunPod (including the retro OS TUI, live generation-while-playing, setlist system, MIDI/OSC controllers, visualizers, and self-healing tools).

## Why RunPod for forage-dj?

- Heavy AI audio generation (Stable Audio 3 medium + LoRAs) benefits greatly from dedicated GPUs.
- Large model files (~ dozens of GB with all variants + LoRAs) should live on **Network Volumes** so you don't re-download every pod.
- The retro OS interface (`python -m foragedj.os`) runs beautifully in a browser-based terminal on RunPod.
- Perfect for "walk away and come back to generated libraries" or live autonomous DJ sessions.

## Recommended Deployment Architecture

1. **Network Volume** (persistent storage for `checkpoints/`, HF cache, libraries, generated sets).
2. **Pod Template** based on PyTorch (with CUDA).
3. **Pre-start script** that clones the repo (or uses a pre-built image), installs everything, and mounts the volume at `/workspace`.
4. **Optional**: Serverless endpoint if you want to expose generation as an API for agents.

## Prerequisites (on your local machine)

```bash
# Install runpodctl
curl -sSL https://cli.runpod.net | bash

# Login (creates ~/.runpod/config.toml with your API key)
runpodctl doctor
```

Get your API key from: https://www.runpod.io/console/user/settings

## Step-by-Step: Create a Persistent forage-dj Pod

### 1. Create a Network Volume (do this once)

Use a large volume (100GB+ recommended for all models + generated libraries).

```bash
runpodctl network-volume create \
  --name "forage-dj-storage" \
  --size 200 \
  --data-center-id "US-GA-1"   # or your preferred region
```

Note the volume ID (e.g. `abc123xyz`).

### 2. Create a Custom Template (recommended)

Use an official PyTorch template as base, then customize.

```bash
# List good base templates
runpodctl template search pytorch --type official --limit 10
```

Example creation (adjust image to latest CUDA + PyTorch):

```bash
runpodctl template create \
  --name "forage-dj-pytorch" \
  --image "runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04" \
  --container-disk-in-gb 50 \
  --volume-in-gb 0 \
  --volume-mount-path /workspace \
  --ports "22/tcp,8888/tcp,7860/tcp" \
  --env "JUPYTER_PASSWORD=sonic" \
  --docker-start-cmd "bash -c 'cd /workspace && git clone https://github.com/Sonic-Forage/forage-dj.git && cd forage-dj && ./scripts/setup.sh --full && python -m foragedj.os'" \
  --readme "forage-dj Music Diffusion OS - see https://github.com/Sonic-Forage/forage-dj"
```

Save the template ID.

### 3. Create the Pod (mounting your volume)

```bash
runpodctl pod create \
  --name "forage-dj-main" \
  --template-id <your-template-id> \
  --gpu-id "NVIDIA GeForce RTX 4090" \
  --gpu-count 1 \
  --network-volume-id <your-volume-id> \
  --volume-mount-path /workspace \
  --public-ip true \
  --cloud-type "SECURE"
```

This will give you a pod with:
- Your persistent storage at `/workspace`
- forage-dj already cloned and set up
- The OS interface ready to boot

### 4. Access the Pod

- SSH: Use `runpodctl ssh info <pod-id>`
- Browser terminal: Go to the pod page on runpod.io
- Web UIs (if exposed): Use the proxy URLs like `https://<pod-id>-7860.proxy.runpod.net`

Inside the pod, launch the full retro OS:

```bash
cd /workspace/forage-dj
uv run python -m foragedj.os
```

Or use the normal CLI:

```bash
uv run foragedj doctor --heal
uv run foragedj live --manifest setlists/your-set.yaml --lookahead 2
```

## Important: Large Models & Storage Strategy

- Always mount a **Network Volume** at `/workspace`.
- Run `foragedj download-models` **once** on the volume (it will use the Z:-style cache logic if you adapt the scripts).
- Subsequent pods reuse the same volume → instant startup with all models + LoRAs + your generated libraries.

## Serverless Option (for Agentic API)

If you want agents to call generation remotely:

1. Create a serverless endpoint from a hub repo or custom worker that wraps forage-dj generation.
2. Expose endpoints for:
   - Generate from prompt + seed
   - Generate full setlist from manifest
   - Status of running pods

See the main project docs for agent integration patterns.

## Common RunPod + forage-dj Patterns

- Use **Secure Cloud** for production.
- Set `--idle-timeout` high if doing long autonomous generation sessions.
- For the retro OS TUI: Use the browser terminal or SSH + tmux.
- Expose port 7860 if you add a Gradio/Tauri UI later.
- Use the self-healing `doctor --heal` after every pod start.

## Troubleshooting

- Models not found → Make sure volume is mounted at the correct path and `download-models` was run at least once.
- Slow first generation → Models are being loaded from disk into VRAM.
- Permission issues → The setup script handles most of this.

## Links

- Main project: https://github.com/Sonic-Forage/forage-dj
- RunPod Console: https://www.runpod.io/console
- runpodctl docs: Use `runpodctl --help` or ask an agent with this skill.

This skill makes deploying the full "Music Diffusion OS" experience on RunPod as close to one-command as possible.
