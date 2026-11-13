#!/bin/bash
# Entry point of the swarm service: start a private Ollama on the assigned GPU(s), then run the given
# harness command from /scratch/AI-Human-Interaction. Example (on hssh1):
#   submit --gpus 1 --name ahi-e1-gptoss eidos-service.di.unito.it/chiesa/ahi-runner:0.20.1 \
#       harness/batch.py --exp E1 --models gpt-oss:20b --reps 3 --workers 3
# Output also goes to /scratch/AI-Human-Interaction/results/logs/<hostname>.log.
set -u
PROJ=/scratch/AI-Human-Interaction
export HOME=/tmp/home && mkdir -p "$HOME"
mkdir -p "$PROJ/results/logs"
LOG="$PROJ/results/logs/$(hostname).log"
exec > >(tee -a "$LOG") 2>&1

export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS="$PROJ/.ollama/models"
export OLLAMA_CONTEXT_LENGTH=65536 OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-3}" OLLAMA_KEEP_ALIVE=-1
export OLLAMA_FLASH_ATTENTION=1 OLLAMA_NOPRUNE=1 OLLAMA_MAX_LOADED_MODELS=1

echo "[$(date)] host=$(hostname) gpu=${DOCKER_RESOURCE_GPU:-?}"
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader 2>&1
ollama serve > /tmp/ollama.log 2>&1 &
for _ in $(seq 120); do ollama list > /dev/null 2>&1 && break; sleep 1; done
ollama list || { echo "ollama did not start"; tail -50 /tmp/ollama.log; exit 1; }

cd "$PROJ"
export AHI_INPROC=1 AHI_RUN_TMP=/tmp/ahi-runs AHI_OLLAMA_URL=http://127.0.0.1:11434
python3 "$@"
rc=$?
echo "[$(date)] exit=$rc"
grep -E "offload|layers to GPU|device=CPU" /tmp/ollama.log | tail -5
exit $rc
