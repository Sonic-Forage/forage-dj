# Feature Implementation Prompts for ForageDJ

## Adding a New CLI Command
"Implement a new subcommand `foragedj analyze-setlist` that loads a manifest and prints energy arc, key compatibility, and recommended transitions. Follow the existing CLI patterns in cli.py and add proper tests."

## Workstation Region Regeneration
"Extend the workstation so that `workstation-regenerate` can optionally use a different model (e.g., small-sfx for percussion regions) while keeping the rest of the track. Update the Region dataclass and regeneration logic."

## MIDI Learn Improvements
"Improve the MIDI learn flow so that it can learn multiple controls in one session and saves mappings to a project-specific file instead of only globally. Update hardware/midi.py and the CLI handler."

## Adding a New Model Backend
"Create support for loading models from a custom local folder structure (not just the official HF layout). This should allow users to use their own fine-tuned Stable Audio models easily."

## Voice Command Router
"Build a more robust intent parser for voice commands. Use a small local LLM to classify user speech into actions like 'generate track', 'auto mix', 'drop SFX', etc., and wire it into the existing voice.py system."

These prompts are designed to be copy-pasted when asking swarm agents or other AIs to implement new features while staying consistent with the existing architecture and culture.