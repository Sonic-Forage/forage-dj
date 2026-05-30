# Docker Deployment for Autonomous Sessions

**Goal**: Run Sonic Forage as a reliable, scheduled, headless "autonomous DJ brain" that can boot itself with enough time to load heavy models, generate or prepare sets, and perform at a specific show time (e.g. 8pm set starts at 7:30 container boot).

This is especially powerful for:
- Dedicated event machines at clubs / warehouses
- Tour rigs that need to be reliable
- 24/7 or scheduled "seed bombing + distribution" machines
- Multi-venue autonomous installations

## Architecture Overview

- **Host machine** (ideally with good GPU + the large Z: drive mounted)
- **Docker** with NVIDIA runtime
- **Bind mount** of the entire `/mnt/z/IMF2045/forage-dj` project (critical for checkpoints and generated libraries)
- **Smart entrypoint** that understands scheduled show times and gives the system time to warm up

## Quick Start (Recommended)

```bash
# 1. Build the image
docker compose -f docker/docker-compose.yml build

# 2. For a one-off autonomous run with scheduling
SHOW_TIME=20:00 BOOT_EARLY_MINUTES=45 docker compose -f docker/docker-compose.yml up
```

The container will sleep until the calculated boot window, run full system prep (`doctor` + `rave-prep` style checks), then execute the command you defined.

## Scheduling Options

### Option A: Host Cron (Simplest & Most Reliable)

On the host machine:

```bash
# Edit crontab
crontab -e

# Example: Every Saturday, boot container at 7:15pm for an 8pm show
15 19 * * 6 cd /mnt/z/IMF2045/forage-dj && docker compose -f docker/docker-compose.yml up --abort-on-container-exit --rm
```

### Option B: systemd Timer (for always-on machines)

Create a service + timer that starts the container at the desired lead time.

### Option C: Inside the container (more advanced)

You can also run a long-running container with an internal scheduler (e.g. using `supercronic` or Python APScheduler) that triggers different autonomous commands at different times.

## Example Autonomous Workflows

### 1. Scheduled 8pm Live Set (with lookahead generation)

```yaml
# In docker-compose.yml environment section
environment:
  - SHOW_TIME=20:00
  - BOOT_EARLY_MINUTES=50
command: >
  live
  --manifest setlists/saturday_night.yaml
  --lookahead 2
```

The container will:
- Wake at ~7:10pm
- Load all models (the slow part)
- Run `rave-prep` style checks
- Start the autonomous live performance at 8pm with tracks already generating ahead

### 2. Nightly Seed Bombing + Distribution Machine

```yaml
environment:
  - SHOW_TIME=03:00          # Run in the middle of the night when machine is idle
  - BOOT_EARLY_MINUTES=20
command: >
  swarm-distribute
  --input sessions/RecentGigs
  --mode full
  --seed-bomb
```

This machine can autonomously:
- Compile new material from recent sessions
- Prepare distribution packages
- Seed bomb fresh generative content to `public/seeds/`
- (Future) push to IPFS / your own distribution endpoint

### 3. Pre-Event Full Generation + Tagging

Useful before a big 12-hour donut rave:

```bash
# Host cron entry
0 10 * * 6 cd /mnt/z/IMF2045/forage-dj && \
  SHOW_TIME=20:00 BOOT_EARLY_MINUTES=90 docker compose -f docker/docker-compose.yml up --abort-on-container-exit
```

Gives the system 90 minutes to generate a full setlist, tag everything, and have it ready by doors.

## Volume Mount Strategy (Very Important)

Because the models are huge, you **must** bind-mount the real project:

```yaml
volumes:
  - /mnt/z/IMF2045/forage-dj:/workspace/forage-dj:rw
```

This way the container sees all your real checkpoints, sessions, generated libraries, and `public/seeds/`.

Never bake the models into the image.

## GPU Requirements

- NVIDIA driver + `nvidia-container-toolkit` on the host
- At least 12–24 GB VRAM recommended for comfortable medium model + lookahead generation during a live set
- The image is based on CUDA 12.4

## Monitoring & Observability (Future)

For serious autonomous installations you will want:
- Prometheus + Grafana for GPU/memory usage
- Log shipping from the container
- Health check endpoint (the `doctor` command can be exposed)
- Remote kill / restart capability

## Security Notes for Public Installations

- The container should run as a non-root user when possible (future improvement)
- Never expose unnecessary ports
- Consider read-only mounts for checkpoints when you only need generation, not training

## Integration with the Rest of the System

This Docker setup works beautifully with:
- The **Event/Tour System** (`docs/EVENT_TOUR_SYSTEM.md`)
- **Swarm Distribution + Seed Bombing** (`skills/swarm-distribution/`)
- **Harm reduction / donut rave** events (the container can be the reliable "brain" while human performers do their thing)
- **PR/Launch/Streaming swarm** (stream the container output or let it drive chat-controlled sets)

## Next Improvements (Autonomous Roadmap)

- Add a lightweight internal scheduler (so one long-running container can handle multiple shows per week)
- Prometheus metrics exporter
- Web UI / API to schedule future autonomous sessions
- Automatic post-show archiving + seed bombing
- Multi-container setups (one for generation, one for real-time playback)

---

**This is how you turn the Sonic Forage Music Diffusion OS into a reliable, bookable, autonomous performance system that can be deployed at clubs, warehouses, festivals, or even permanent installations.**

You schedule the show. The container wakes up with enough time. The models load. The set is ready. The culture spreads.
