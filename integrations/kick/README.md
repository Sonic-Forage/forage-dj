# Kick Integration for Sonic Forage Workstation

**Goal**: Full autonomous control and chat interaction on Kick.com streams using the official Kick Dev API.

## Key Resources (vendored / referenced here)

- Official Docs: https://github.com/KickEngineering/KickDevDocs (and https://docs.kick.com)
- Alternative wrapper: https://github.com/nekiro/kick-api

## What We Can Do (High Value for Live Performance)

- Listen to chat messages in real-time (via webhooks or polling)
- Let chat suggest prompts for the next region regeneration (`!prompt darker bassline`)
- Moderate / respond to chat
- Get channel info, livestream metadata, viewer count
- Send messages from the autonomous DJ ("Region regenerated based on chat vote")
- Kicks / gifts events for fun interactions
- Categories, tags, custom tags for discovery

## Initial Python Integration Plan (inside this project)

Create `src/foragedj/integrations/kick.py` (or hardware/kick_chat.py) that:

1. OAuth app setup (user creates app at Kick developer portal)
2. Webhook receiver for chat events (or polling for simplicity at first)
3. Command parser that feeds into `workstation.regenerate_region` or `live` mode
4. Bidirectional: DJ can send messages back to chat

## Power Chat Features for Autonomous DJ

- Chat votes on next prompt
- "Auto DJ mode" where the system analyzes chat sentiment/energy and chooses/generates regions
- Reward systems (gifts = special prompt priority)

## Next Steps (Autonomous)

- [ ] Create app registration helper in CLI (`foragedj kick-auth`)
- [ ] Basic chat listener + prompt queue
- [ ] Hook into existing `workstation` and `live` modes
- [ ] OBS-friendly overlay for "Chat Prompt Queue"

All code and docs stay inside `/mnt/z/IMF2045/forage-dj/integrations/kick/`.

This pairs perfectly with the existing PR/Streaming swarm and the new workstation editing features for live, chat-driven performances.
