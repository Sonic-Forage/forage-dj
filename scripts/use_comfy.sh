#!/bin/bash
# Quick helper to switch ForageDJ to use your main ComfyUI rig (Z:\C0MFY\ComfyUI via Tailscale)
#
# Usage:
#   source scripts/use_comfy.sh
#
# This sets the environment variable that the whole project respects.

export COMFYUI_URL="http://100.99.10.17:8188"

echo "✅ ForageDJ now pointed at your main ComfyUI rig via Tailscale"
echo "   COMFYUI_URL=$COMFYUI_URL"
echo ""
echo "You can also make this permanent by running:"
echo "  python -c 'from src.foragedj.config import load_config, save_config; c=load_config(); c.setdefault(\"generation\", {})[\"default_backend\"]=\"comfy\"; c.setdefault(\"generation\", {})[\"comfy_url\"]=\"http://100.99.10.17:8188\"; save_config(c); print(\"Config updated!\")'"
echo ""
echo "Then just do:  foragedj generate \"your prompt\" --duration 30"
echo "(no --backend flag needed — comfy is now the default)"