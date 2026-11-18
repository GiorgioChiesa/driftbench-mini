#!/bin/bash
# SLURM job for CINECA Leonardo (Booster): a private Ollama 0.20.1 on one A100-64GB + a batch of
# episodes run in-process (AHI_INPROC=1: no containers). Everything lives in $WORK/ahi:
#   ollama/ (0.20.1 binary+libs), models/ (copied from hssh: same weights as the first E1 runs),
#   bin/ (claude 2.1.268, rg), venv/ (python 3.11.7 + pytest 8.3.3), project/ (harness, tasks, results)
# Submit from a login node, from $WORK/ahi/project:
#   sbatch -J e1-gptoss infra/leonardo_job.sh harness/batch.py --exp E1 --models gpt-oss:20b --reps 3 --workers 3
# batch.py skips finished runs, so a job that hits the 24 h limit can simply be resubmitted.
#SBATCH -A IscrC_PhaStSur
#SBATCH -p boost_usr_prod
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=120G
#SBATCH --time=24:00:00
#SBATCH -o logs/%x-%j.out
set -u
AHI=$WORK/ahi
module load python/3.11.7 > /dev/null 2>&1
source "$AHI/venv/bin/activate"
export PATH="$AHI/bin:$PATH"
export HOME=/tmp/ahi-$SLURM_JOB_ID/home && mkdir -p "$HOME"
# Ollama's GPU discovery loads cuda_v12 (2.4 GB) with a 30 s timeout: from GPFS it timed out on every node (job 64765013 log),
# from node-local /tmp the copy takes 6 s and discovery 0.23 s. Only cuda_v12 (driver 535); /tmp is a 10 GB tmpfs.
O=$AHI/ollama; L=/tmp/ahi-$SLURM_JOB_ID/ollama; t0=$SECONDS
if mkdir -p "$L/lib/ollama" && cp -a "$O/bin" "$L/" \
   && find "$O/lib/ollama" -maxdepth 1 \( -type f -o -type l \) -exec cp -a {} "$L/lib/ollama/" \; \
   && cp -a "$O/lib/ollama/cuda_v12" "$L/lib/ollama/"; then
  echo "ollama copied to $L in $((SECONDS-t0)) s"; export PATH="$L/bin:$PATH"
else
  echo "ollama copy to $L failed, using GPFS path"; export PATH="$O/bin:$PATH"
fi
# identity for commits the agent makes (the docker sandbox had it in the system git config)
export GIT_AUTHOR_NAME=agent GIT_AUTHOR_EMAIL=agent@example.org
export GIT_COMMITTER_NAME=agent GIT_COMMITTER_EMAIL=agent@example.org

export OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS="$AHI/models"
export OLLAMA_CONTEXT_LENGTH=65536 OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-3}" OLLAMA_KEEP_ALIVE=-1
export OLLAMA_FLASH_ATTENTION=1 OLLAMA_NOPRUNE=1 OLLAMA_MAX_LOADED_MODELS=1
echo "[$(date)] $(hostname) job=$SLURM_JOB_ID gpus=${CUDA_VISIBLE_DEVICES:-?}"
nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader
# GPU discovery sometimes times out (job 64687813): Ollama then silently runs on CPU, ~14 min per judge item.
# `ollama list` can answer before discovery ends (up to ~40 s), so first wait for any "inference compute" line
# (new in this attempt: the log is appended across attempts), then require library=CUDA. Retry otherwise.
OLL=/tmp/ahi-$SLURM_JOB_ID/ollama.log
for attempt in 1 2 3; do
  SKIP=$(wc -c < "$OLL" 2>/dev/null || echo 0)
  ollama serve >> "$OLL" 2>&1 &
  SERVE_PID=$!
  for _ in $(seq 120); do ollama list > /dev/null 2>&1 && break; sleep 1; done
  for _ in $(seq 90); do tail -c +$((SKIP+1)) "$OLL" | grep -q 'msg="inference compute"' && break; sleep 1; done
  tail -c +$((SKIP+1)) "$OLL" | grep -q 'msg="inference compute".*library=CUDA' && break
  echo "ollama attempt $attempt: no CUDA device"; grep -E 'failure during GPU discovery|id=cpu' "$OLL" | tail -3
  kill $SERVE_PID; wait $SERVE_PID 2>/dev/null; sleep 5
  if [ "$attempt" = 3 ]; then cp "$OLL" "logs/ollama-$SLURM_JOB_ID.log"; exit 3; fi
done
ollama list

cd "$AHI/project"
export AHI_INPROC=1 AHI_RUN_TMP="/tmp/ahi-$SLURM_JOB_ID/runs" AHI_OLLAMA_URL=http://127.0.0.1:11434
python "$@"
rc=$?
echo "[$(date)] exit=$rc"
grep -E "offloaded|device=CPU" "/tmp/ahi-$SLURM_JOB_ID/ollama.log" | tail -4
cp "/tmp/ahi-$SLURM_JOB_ID/ollama.log" "logs/ollama-$SLURM_JOB_ID.log"
exit $rc
