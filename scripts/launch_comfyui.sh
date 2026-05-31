#!/bin/bash
# Quick launcher for ComfyUI server using the project's Docker setup.
# This gives you a reliable inference server for Stable Audio models
# using your local Z: drive checkpoints (including optimized TensorRT/ONNX versions).

set -e

cd "$(dirname "$0")/.."

echo "Starting ComfyUI (profile: comfy)..."
docker compose -f docker/docker-compose.yml --profile comfy up -d comfyui

echo ""
echo "ComfyUI is starting at http://localhost:8188 (also reachable as http://0.0.0.0:8188 on this host)"
echo ""
echo "Recommended next steps inside the UI:"
echo "  1. Install ComfyUI-Manager if not present"
echo "  2. Use Manager to install nodes for Stable Audio Open (search 'StableAudio' or 'Stable Audio Open')"
echo "  3. For your optimized models, also install any TensorRT / ONNX custom nodes"
echo ""
echo "Workflows folder: workflows/comfy/  (mounted into container + used by ForageDJ client)"
echo "  python -c 'from src.foragedj.comfy_client import generate_via_comfy; print(generate_via_comfy(\"test prompt\", duration=8))'"
echo ""
echo "To stop ComfyUI: docker compose -f docker/docker-compose.yml --profile comfy down"