# Deploying forage-dj on RunPod (Manual + Automated)

This guide covers getting the full **forage-dj Music Diffusion Operating System** running on RunPod cloud GPUs, including the retro OS interface, live autonomous DJ mode, all models/LoRAs, and agentic tools.

## Recommended Architecture

- Use a **Network Volume** for `checkpoints/`, HF cache, libraries, and generated sets (models are large — never re-download).
- Base on an official **PyTorch CUDA** template.
- Mount the volume at `/workspace`.
- Run the project from there.

## Step-by-Step Manual Deployment

### 1. Get a RunPod Account + API Key

1. Sign up at [runpod.io](https://www.runpod.io)
2. Go to **User Settings → API Keys** and create a key (save it securely).

### 2. Install runpodctl (recommended)

```bash
curl -sSL https://cli.runpod.net | bash
```

Then run `runpodctl doctor` and follow the prompts to add your API key.

### 3. Create a Persistent Storage Volume

```bash
runpodctl network-volume create \
  --name forage-dj-main \
  --size 200 \
  --data-center-id US-GA-1
```

Note the volume ID.

### 4. Create the Pod

Use the RunPod web UI or CLI.

**Recommended settings:**
- **Template**: Any recent "PyTorch" official template (e.g. with CUDA 12.4+ and Python 3.11/3.12)
- **GPU**: RTX 4090, A6000, or better (depending on whether you want medium model + LoRAs comfortably)
- **Container Disk**: 50GB+
- **Network Volume**: Attach the one you created above, mounted at `/workspace`
- **Ports**: Expose at minimum 22 (SSH) and 7860 (if you add a web UI later). You can expose more.

After the pod is running:

```bash
# SSH in (use runpodctl ssh info <pod-id> for the command)
cd /workspace

# Clone the project (or use a pre-built image later)
git clone https://github.com/Sonic-Forage/forage-dj.git
cd forage-dj

# One-time setup (this will install everything including the OS interface)
./scripts/setup.sh --full

# Download all models + LoRAs to the persistent volume (this can take a while the first time)
export HF_TOKEN=your_token_here
uv run foragedj download-models

# Boot the full retro OS
uv run python -m foragedj.os
```

You now have the complete old-school computer interface running in the browser terminal on RunPod.

## Using the Self-Healing Tools on the Pod

```bash
uv run foragedj doctor --heal
uv run foragedj live --manifest setlists/bassline_dominion_seed424242.yaml --lookahead 2
```

## Automated Deployment (with API Key)

See the companion skill at `skills/runpod-forage-dj/SKILL.md`.

A future `scripts/runpod_deploy.py` will be able to take your `RUNPOD_API_KEY` and automatically:
- Create or reuse a network volume
- Create a pre-configured pod with forage-dj already set up
- Optionally start the OS interface or a serverless endpoint

(Work in progress — the skill document above contains the current best patterns.)

## Tips for Best Experience

- Always use Network Volumes for the `checkpoints/` directory.
- The first model download is slow — subsequent pods using the same volume are fast.
- For the retro OS TUI, the RunPod web terminal works great.
- For heavy autonomous generation sessions, choose higher vCPU + more RAM pods.
- You can expose ports and access the visualizer or future web UIs via `https://<pod-id>-<port>.proxy.runpod.net`

## Linking Back to the Main Project

All development happens in the main repo:
https://github.com/Sonic-Forage/forage-dj

When you deploy on RunPod, you're running the exact same codebase + your local models/LoRAs moved to the cloud volume.

## Need Help?

- Use the skill with any compatible AI agent: `npx skills add runpod/skills` then ask about the forage-dj skill.
- Open an issue in the main repo.
- The self-healing `doctor --heal` command is your friend on the pod.

Welcome to the cloud version of the Music Diffusion OS.
