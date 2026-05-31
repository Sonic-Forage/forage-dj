# How to Use This Workspace Remotely (Hermes or Other Agents)

## Goal

A remote Hermes agent (or any other capable agent) should be able to be pointed at this folder and meaningfully continue the work without needing the full conversation history.

## Recommended Way

1. Give the remote Hermes agent access to the entire ForageDJ project (via git, shared volume, etc.).

2. Tell it to start here:
   ```
   /path/to/forage-dj/agent/hermes-comfy-autonomous/AGENT_START_HERE.md
   ```

3. Instruct it to:
   - Read the full `AGENT_START_HERE.md`
   - Read `CURRENT_DIRECTION.md` and `BRANCH_STRATEGY.md`
   - Look at `AUTONOMOUS_TASKS.md` for current work
   - Check the corresponding `sessions/` folder in the project root for detailed manifests

## Useful Environment Variables / Context to Provide

- The current active ComfyUI server URL (if any)
- Whether the agent should prefer working on `main`, `beta`, or the legacy branch
- Any specific remote ComfyUI pod details (if relevant)

## What This Folder Is Not

- It is **not** a replacement for the full project.
- It is a **focused, high-signal context pack** for an agent working on the ComfyUI autonomous direction.

## Bonus

If you're using Hermes, you can also give it access to the `forage-comfy` skill at:
`.grok/skills/forage-comfy/`

The skill + this workspace together give a remote agent a very strong position to operate from.
