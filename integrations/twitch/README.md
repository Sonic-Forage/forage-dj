# Twitch Integration for Sonic Forage Workstation

**Resources**:
- Official: https://github.com/twitchdev
- API topics & samples: https://github.com/topics/twitch-api
- EventSub, IRC, Helix API for chat, channel points, predictions, etc.

## High-Value Features for Autonomous Live

- Chat command integration (`!region darker techno drop`)
- Channel Points redemptions that trigger specific regenerations or effects
- Predictions on what the next section will sound like
- Real-time hype chat energy analysis → influence generation parameters
- Stream markers + clip creation tied to great generated moments

## Plan

- `src/foragedj/integrations/twitch.py` stub
- EventSub webhook receiver (recommended over IRC for modern apps)
- Command router that feeds directly into the workstation / live autonomous DJ

This + Kick gives us "access to all platforms" for chat-driven autonomous performances.

Everything contained in the project root.
