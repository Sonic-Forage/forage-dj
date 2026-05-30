# Avatars & Reactive Characters – Avaturn Integration

**Repo**: https://github.com/avaturn-live/avtr-1

## Vision (Bad Ass)

Create living visual companions for the Sonic Forage Workstation:

- 3D/2D characters that **listen to the music** in real time
- Bob, dance, react emotionally to the current region / energy / prompts
- Small UI overlays that pop up ("This drop is hitting different 🔥")
- Encourage creation: "Want to make your own avatar? Tune it on our dataset"
- Autonomous DJ avatars that "perform" alongside the generated music

## Why This is Perfect for the Project

- Turns pure audio into a full audiovisual experience for streams, raves, clubs, festivals
- Workshop-friendly: People can create custom characters on-site
- Ties beautifully into the new workstation (regions have visual avatars that change when regenerated)
- Monetization angle: Custom avatar packs, shared community characters with royalties

## Technical Path

1. **Current**: Use Avaturn to generate characters
2. **Integration points**:
   - Feed audio features (BPM, energy, key, onset strength from our `analysis.py`) into the avatar
   - Send current prompt / region metadata
   - Real-time parameter driving (head bob intensity, emotion based on prompt sentiment)
3. **Dataset tuning**: Collect our own generated + performed music + motion data to fine-tune reactive models

## Next Autonomous Steps

- Create `src/foragedj/integrations/avaturn.py` stub
- Add "Avatar Layer" toggle in the retro OS and workstation-view
- Simple OSC bridge (we already have OSC) to drive external avatar software
- Research fine-tuning pipeline for Avaturn / similar models with our local dataset

This is one of the coolest "embrace the tech at raves and workshops" directions.

All files inside the project root on the mounted drive.
