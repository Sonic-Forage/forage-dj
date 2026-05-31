# Debugging Prompts for ForageDJ

## CLI / Doctor Issues
"Run `uv run foragedj doctor --heal` and analyze any warnings or errors. Focus on model loading, HF token, and path containment issues. Suggest fixes that keep all data on the Z: drive."

## Generation Failures
"The `generate` command is failing with [paste error]. Debug the audio_gen.py loading logic, check if the local checkpoint is being used correctly, and ensure the HF token from .grok/hf-token.env is being picked up."

## Mixer / Real-time Issues
"Investigate latency or crackling in the mixer. Check the audio callback in mixer.py, buffer sizes, and any pedalboard processing. Suggest optimizations for potato machines."

## Path Containment Violations
"Search the codebase for any hardcoded paths that bypass paths.py. Ensure all generated data, checkpoints, and caches stay under the configured data root (Z: drive)."

Use these when an agent is troubleshooting or when you need systematic debugging help.