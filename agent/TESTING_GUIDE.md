# 🧪 TESTING_GUIDE.md - How to Test ForageDJ Autonomously

## Quick Local Test Commands

```bash
# 1. Fresh install
uv sync --extra cpu

# 2. Basic CLI test
uv run foragedj --version

# 3. Generate a test track (Phase 1)
uv run foragedj generate "dark techno 128bpm" --seed 42 --duration 30

# 4. Test mixer (Phase 2)
uv run foragedj mix track1.wav track2.wav --crossfade 8

# 5. Launch GUI (Phase 3)
uv run foragedj gui
```

## Potato Machine Test Checklist

- [ ] Install completes in <5 minutes on CPU-only
- [ ] Generation of 30s track takes <90 seconds
- [ ] Real-time mixer runs at <10ms latency
- [ ] GUI opens without GPU
- [ ] No crashes on low RAM (4-8GB)

## Full End-to-End Test (MVP)

1. Generate 3 tracks from a setlist
2. Load into two decks
3. Mix live for 2 minutes
4. Export the mix
5. Verify audio quality and transitions

**If anything fails, create a GitHub issue with logs.**

**You are cleared for autonomous testing.**