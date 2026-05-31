# What Worked (Institutional Memory)

## The Pivot to ComfyUI

- Accepting that ComfyUI (especially with strong workflows like ACE-Step 1.5 XL Turbo) produces significantly better results than the Python Stable Audio path was the correct call.
- Quality is now the north star instead of "make the Python models work."

## The `forage-comfy` Skill

- Creating a dedicated, self-documenting skill for ComfyUI interaction has been very effective.
- The pattern of combining references/ + executable scripts/ + a strong SKILL.md gives agents deep, actionable knowledge.

## Terminal Radio Concept

- The idea of a "realtime radio" that the user can leave running in the background while they code or work has been very well received.
- Both the web player and the PowerShell TUI versions showed promise.

## Remote + Local Flexibility

- Designing the system so it doesn't assume the ComfyUI server is always on the same machine as the user has been valuable (even if not fully realized yet).

## Autonomous Sessions Pattern

- Using the `sessions/` folder + `session.json` manifests to define autonomous work packages has proven to be a good way to hand off work to future agents or swarm runs.

## Preserving History on Branches

- Creating the `legacy/stable-audio` branch early in the pivot preserved a lot of valuable work and experiments without polluting the new direction.

## Using the User's Actual Workflows

- Working directly with the user's real ACE-Step and Stable Audio 3 Medium blueprints (instead of only toy examples) has been much more useful than building in a vacuum.

---

**Lesson**: When the user has a powerful existing tool (their customized ComfyUI rig + workflows), the highest-leverage path is usually to integrate with it deeply rather than trying to rebuild equivalent functionality inside the project.
