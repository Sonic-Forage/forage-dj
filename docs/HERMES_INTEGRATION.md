# Hermes Agent Integration for forage-dj

Sonic-Forage is explicitly built to be consumed by autonomous agents (see the org card on HF and the starter kit).

## Current Integration Points (usable today)

- **CLI as tools**: Every subcommand (`generate`, `generate-setlist`, `download-models`, `doctor`, etc.) can be called by an agent.
- **Manifests as structured input**: YAML/JSON setlists are perfect for agents to plan, modify, and version.
- **library.json output**: Rich metadata (BPM, key, energy, transitions) that agents can reason over.
- **Z: drive + local checkpoints**: Agents can work fully offline after one download.

## Recommended Tool Schema for Hermes-style Agents

```json
{
  "name": "forage_dj_generate_setlist",
  "description": "Generate a full locked-seed setlist from a manifest and return the organized library path + summary.",
  "parameters": {
    "type": "object",
    "properties": {
      "manifest_path": {"type": "string"},
      "dry": {"type": "boolean", "default": false}
    }
  }
}
```

Similar tools for:
- download_models
- play_library (headless mixer mode)
- export_dataset (for retraining)

## Long-term Vision

An agent (or swarm of agents) that can:
- Curate prompts from real-world data (weather, news, social sentiment, previous gig feedback)
- Generate overnight libraries
- Self-curate training datasets from successful sets
- Propose bookings (human-in-the-loop approval gate)
- Iterate on its own style via LoRA fine-tuning loops

This is exactly why we built the system the way we did.

## Getting Started with Hermes + forage-dj

See the official Hermes Agent repo: https://github.com/nousresearch/hermes-agent

Example starter (future):
- Expose forage-dj CLI as a tool server
- Give the agent access to the `setlists/` and `libraries/` folders on Z:
- Let it plan multi-day festival runs

---

*Built for agents. Designed for humans. Given away in the spirit of PLUR.*
