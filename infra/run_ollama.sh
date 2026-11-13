#!/usr/bin/env bash
# Dedicated Ollama server for this project (GPUs 2,3; localhost:11500). Models live in ../.ollama
# Pinned to 0.20.1: hssh1 has NVIDIA driver 535 and Ollama >= 0.30 requires >= 550 (it silently
# falls back to CPU); 0.20.1 still runs on CUDA and has the Anthropic-compatible /v1/messages API.
# KEEP_ALIVE=30m (not 24h): the A40s are shared, so idle models must release VRAM.
# Note: env vars only take effect when the container is (re)created with this script.
set -euo pipefail
B="$(cd "$(dirname "$0")/.." && pwd)"
docker run -d --name ahi-ollama --restart unless-stopped --gpus '"device=2,3"' \
  -p 127.0.0.1:11500:11434 -v "$B/.ollama:/root/.ollama" \
  -e OLLAMA_CONTEXT_LENGTH=65536 -e OLLAMA_NUM_PARALLEL=3 -e OLLAMA_KEEP_ALIVE=30m -e OLLAMA_MAX_LOADED_MODELS=2 \
  -e OLLAMA_FLASH_ATTENTION=1 \
  ollama/ollama:0.20.1
