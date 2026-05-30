# Live Streaming & Performance Guide — Sonic Forage Workstation

**Goal**: Get you from "I just installed this" to "I'm live on Twitch/Kick performing with a fully local AI music workstation" with minimal pain.

## Why This Tool Is Uniquely Good for Streaming

- Fully local → no latency to cloud, no usage limits, full privacy
- The workstation features let you **edit live** (regenerate regions on the fly while the set is playing)
- Retro OS + terminal visuals look distinctive and cool
- Chat can directly influence the music in real time
- You own everything and quality only gets better

## Quick Start: Be Live in < 15 Minutes

1. Make sure you're set up:
   ```bash
   source .grok/hf-cache.env
   uv run foragedj doctor --heal
   ```

2. Prepare a session or setlist in advance (or generate live).

3. Launch the retro OS (best visuals):
   ```bash
   uv run foragedj os
   ```

4. In another terminal/pane, run the arrangement view or live mode.

5. Capture in OBS using the recommendations below.

## Recommended OBS Setup

### Basic Scenes

- **Main Performance**: Retro OS in full screen or large window + big current prompt overlay
- **Arrangement View**: `foragedj workstation-view` in a dedicated capture (shows your regions live)
- **Technical**: Visualizer waveform + small terminal for status
- **Chat Interaction**: Split view with chat on the right

### Capture Tips for Clean Looks

- Use a good monospace font (JetBrains Mono, Fira Code, or Cascadia Code) at 18-26pt
- The default green-on-black retro theme captures very well
- Consider a slight transparency or solid dark background behind the terminal
- For the workstation-view, make the terminal wide (140+ columns) so the timeline looks good

### Audio Routing

- Route the mixer output (`foragedj live` or the OS player) to a virtual cable if you want separate game/chat audio
- On Windows: VB-Audio Cable or similar
- On Linux: PipeWire + easyeffects or Helvum for routing

## Making It Interactive (The Killer Feature)

Viewers love feeling like they have influence.

**Simple version (manual but effective)**:
- Keep an eye on chat
- When someone suggests something cool, use `workstation-regenerate` on the current region or next one

**More advanced (Nightbot / StreamElements)**:
- Create a `!prompt` command that queues suggestions
- You review and trigger them live

**Future (when we add it)**:
- Actual chat-to-prompt bridge so viewers can directly queue region changes

Example stream title that works well:
"Local AI Music Workstation — Chat Controls the Next Region (Twitch Plays Diffusion)"

## Performance Workflow (Proven Pattern)

1. Start with a strong base session or generate the first 1-2 tracks live.
2. Play using the real-time mixer or live mode.
3. When energy drops or chat wants a change → switch to workstation-view, pick a region, regenerate with new prompt.
4. The new audio drops in (with enhancement) and you crossfade or jump to it.
5. Repeat. The set evolves in real time based on the room.

This is genuinely more interesting to watch than pure generation or pure DJing.

## Hardware & Latency Notes for Live

- For best results: Decent GPU for generation + good CPU for the real-time mixer.
- Use the small/optimized models when performing live.
- Pre-generate a safety net of 4-6 tracks before going live.
- The `--lookahead` in live mode helps a lot.
- Test your exact chain (generation + enhancement + playback) before the stream.

## Common Issues & Quick Fixes for Streams

- **Terminal looks bad on stream**: Bigger font, wider terminal, high contrast theme.
- **Generation too slow on stream**: Use smaller models or pre-generate more material.
- **Chat can't see what's happening**: Show the workstation-view or big prompt text prominently.
- **Audio crackles**: Lower blocksize in the mixer if needed, or use a dedicated audio interface.

## Long-Term Vision for Live Use

- Full chat-controlled region system
- Multi-user collaborative sessions (multiple people shaping one performance)
- IRL / club use via RunPod or powerful local rig + good controllers (we already have MIDI/OSC foundation)
- "24 hour generative performance" type spectacles

## Resources

- Main project root: everything lives in `/mnt/z/IMF2045/forage-dj/`
- `skills/pr-launch-and-streaming/SKILL.md` — for the swarm working on this
- `docs/WORKSTATION.md` — deep dive on the editing features
- `docs/INSTALL.md` — cross-platform setup

---

**You don't need perfect quality to start streaming.**  
The story of "local, private, editable, and getting better every week" is compelling on its own — especially when viewers can see the edits happen live.

Go make some noise. 📺🍓🎛️

(Contributions to this guide and the stream-ready features are extremely welcome.)
