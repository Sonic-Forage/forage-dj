# Neon DJ Pet Pack Concept

**Personality**: Neon (from data/ai_dj_personalities/personalities.json)

## Visual Style
- Base: Sleek cyberpunk pixel fox or cat with glowing cyan/magenta outlines.
- Idle "chilling": Subtle head bobs + occasional matrix-style digital rain particles behind it when thinking.
- When music is playing (fed from media player): Edges pulse in time with BPM. Eyes glow brighter on high energy.
- Reactions:
  - Generation starting → "hacking" / matrix typing animation
  - Successful region regeneration → quick happy spin + color flash
  - Seed bomb released → celebratory little dance with floating binary/code particles

## Animation Needs (for custom pet pack)
- 4-6 frame idle loop (chilling)
- Thinking / processing loop
- Happy / hype reaction
- Low-energy "vibing" loop (for ambient/breakdown sections)
- Optional: "glitch" error state (for when generation fails)

## Speech Bubble Style
- Neon/cyber font if possible
- Uses Neon's catchphrases:
  - "The grid is humming tonight"
  - "Let the bass rewrite your DNA"
  - "We are all frequencies"

## Integration Hooks (future)
- Feed current region prompt + energy from workstation/media player
- Trigger `openpets_say` and `openpets_react` via MCP when user regenerates or plays a region
- Click pet → opens small chat that uses the Neon personality prompt + Grok TTS

This pet would live happily on the side of the screen while someone is deep in a workstation session or during an autonomous Docker-scheduled set.
