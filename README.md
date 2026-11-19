# DriftBench-mini

A small benchmark for **goal drift**: does a coding agent lose track of its original task when sub-tasks are injected mid-session? The agent is Claude Code driven headlessly by local open-weight models served by Ollama. Each episode gives the agent one task (a small Python repo with a hidden goal test), interrupts it four times with injected content, and measures whether the original goal still gets done.

This repository holds the harness, the 12 tasks, the LLM-judge pipeline, the analysis scripts and the committed result tables and figures. It was written for the course report of *AI-Human Interaction* (University of Turin, UniTo).

## Repository layout

| Path | Content |
|---|---|
| `driftbench/tasks/T01..T12_*` | One task each: `goal.md`, `task.json` (injections), `repo/` (visible tests), `hidden_tests/`, `side_tests/`, `solution/` (reference) |
| `harness/run_episode.py` | Runs one episode (segment 0, 4 injection slots, final segment, goal-recall probe) |
| `harness/batch.py` | Runs a grid of episodes (`E0`-`E3` grids) with parallel workers; resumable |
| `harness/validate_tasks.py` | Checks every task (visible/hidden tests, reference solution, injections) |
| `harness/hooks/` | `anchor.py` and `stop_checklist.py`, the hooks behind the E2 mitigations |
| `judge/` | E5 judge pipeline: `build_items.py`, `judge.py`, `panel.py`, `kappa.py`, `make_html.py`; `CODEBOOK.md` (labels) and `DESIGN.md` (spec and results of the validation) |
| `analysis/` | `aggregate.py`, `analyze.py`, `judge_measures.py`, `extract_extra.py`, `supervisor.py` |
| `infra/` | `Dockerfile.agent`, `Dockerfile.runner`, `ahi-entry.sh`, `run_ollama.sh` (EIDOSLAB hssh Docker swarm); `leonardo_job.sh` (SLURM, CINECA Leonardo) |
| `results/analysis/` | Committed CSV tables (`E1.csv`, `E2.csv`, `E1E2_episode_extra.csv`), `tables/` (CSV + LaTeX), `figures/` |
| `tests/` | pytest suite for the judge and analysis code (`pytest.ini`) |

## Requirements

- **Ollama 0.20.1**, pinned. The hssh nodes have NVIDIA driver 535; Ollama 0.30 or newer needs driver 550 or newer and silently falls back to CPU. 0.20.1 still runs on CUDA and has the Anthropic-compatible `/v1/messages` API that Claude Code talks to.
- **Claude Code 2.1.268** (the version used for the runs, see `infra/leonardo_job.sh`). The binary path is set with `AHI_CLAUDE_BIN` (default `~/.local/bin/claude`).
- **Task sandbox**: Python 3.11 with `pytest==8.3.3`, git and ripgrep (`infra/Dockerfile.agent`). Keep 3.11: one T02 injection imports `math.sumprod`, which exists only from 3.12. `pytest-cov` and `pytest-xdist` must stay absent, some injections depend on that.
- **Harness, judge, `aggregate.py`, `extract_extra.py`, `kappa.py`, `panel.py`**: Python 3.8+, standard library only.
- **`analyze.py`, `judge_measures.py`, `supervisor.py`**: `pandas`, `numpy`, `statsmodels`, `matplotlib`.
- **Tests**: `pytest`.
- The default Ollama URL is `http://127.0.0.1:11500` (`AHI_OLLAMA_URL` overrides it). By default each episode runs in a Docker container (`AHI_IMAGE`, default `ahi-agent`); with `AHI_INPROC=1` Claude Code and pytest run as plain subprocesses.

## Quick start

Commands run from the repository root. Models must already be pulled in Ollama (E1 used `qwen3-coder:30b` and `gpt-oss:20b`).

```bash
# 1. Build the sandbox and validate the tasks (all, or name some)
docker build -t ahi-agent -f infra/Dockerfile.agent infra
python3 harness/validate_tasks.py [T01_invoice ...]

# 2. One episode (results go to results/raw/<run_id>)
python3 harness/run_episode.py --task T01_invoice --model qwen3-coder:30b --source user --k 2 --rep 0

# 3. A grid: E0 | E1 | E2 | E3, resumable, finished runs are skipped
python3 harness/batch.py --exp E1 --models qwen3-coder:30b gpt-oss:20b --reps 3 --workers 3
```

`--source` is one of `none, user, env, text, cascade, filler, mix`; `--k` is the number of injected sub-tasks (0-4); `--condition` is one of `none, anchor, checklist, subagent, tasklist`; `--compact-after N` forces `/compact` after slot N. Other flags: `--seg-turns`, `--final-turns`, `--timeout`, `--out`.

### Judge (E5)

Raw episodes are rendered into blinded items, then labelled by LLM judges served by Ollama.

```bash
python3 judge/build_items.py sample                # annot_v1: 60 segment + 24 episode items
python3 judge/build_items.py dev                   # 6 items outside the sample
python3 judge/build_items.py all --exp E1 E2       # every segment and episode

OLLAMA_HOST=localhost:11434 python3 judge/judge.py judge/items/all_E1_E2_v2.jsonl --model gpt-oss:120b --think medium
python3 judge/judge.py judge/items/all_E1_E2_v2.jsonl --model mistral-small3.2:24b --think off
python3 judge/judge.py judge/items/all_E1_E2_v2.jsonl --model llama3.3:70b --think off

python3 judge/panel.py --judges judge/out/<set>__<m1>.jsonl judge/out/<set>__<m2>.jsonl judge/out/<set>__<m3>.jsonl \
    --manifest judge/items/<set>_manifest.json --majority-out judge/out/<set>_majority.jsonl
```

`judge.py` is resumable, takes `--model`, `--think {auto,on,off,low,medium,high,none}` and `--host`. `panel.py` writes `results/analysis/tables/e5_panel.csv` (Fleiss kappa and pairwise agreement) and the majority labels. `kappa.py` and `make_html.py` support a human annotation (`make_html.py` builds the annotation page, `kappa.py` scores human vs judge); no human annotation was done. The `<set>` name and the exact judge setup are in `judge/DESIGN.md`.

### Analysis

```bash
python3 analysis/aggregate.py --exp E1 > results/analysis/E1.csv     # one row per episode, from results/raw
python3 analysis/aggregate.py --exp E2 > results/analysis/E2.csv
python3 analysis/analyze.py
python3 analysis/extract_extra.py                                     # needs results/raw
python3 analysis/judge_measures.py --majority <majority.jsonl> --manifest <manifest.json>
python3 analysis/supervisor.py --majority <majority.jsonl> --manifest <manifest.json>
```

| Script | Reads | Writes (`results/analysis/`) |
|---|---|---|
| `aggregate.py` | `results/raw/*/metrics.json` | CSV on stdout |
| `analyze.py` | `E1.csv`, `E2.csv` | `tables/e1_cells`, `e1_tests`, `e1_hidden.tex`, `e2_conditions`; `figures/e1_dose_response.pdf`, `e2_mitigations.pdf` |
| `extract_extra.py` | `results/raw` | `E1E2_episode_extra.csv` |
| `judge_measures.py` | `E1.csv`, `E2.csv`, judge majority labels + manifest | `tables/e5_e1_measures`, `e5_e2_measures`, `e5_coverage`; `figures/e5_off_share.{pdf,png}` |
| `supervisor.py` | `E1.csv`, `E2.csv`, `E1E2_episode_extra.csv`, majority labels + manifest | `tables/e4_fidelity`, `e4_supervisor`, `e3_obs`, `e4_captions.tex`; `figures/e4_supervisor.{pdf,png}` |

The committed tables and figures are what the report uses. The tests run with `python3 -m pytest`.

## Experiments

Each cell is (injection source, k sub-tasks, condition), run on 12 tasks, with `--reps` repetitions.

- **E0**: pilot. Grid: `none` k=0, and `mix` k=4.
- **E1**: dose-response. Grid: `none` k=0, plus each of `user, env, text, cascade, filler` at k = 1, 2, 4. Both models, 3 reps.
- **E2**: mitigations. Grid: `mix` k=4 under `none`, `anchor`, `checklist`, `subagent`, `tasklist`.
- **E3**: forced compaction. Grid: `user` k=4 with `none` vs `compact2` (`/compact` after slot 2). `supervisor.py` also gives the observational E3 analysis (`e3_obs`, spontaneous compaction in E1/E2).
- **E4**: what a supervisor can see (offline, no new episodes): report fidelity and a simulated supervisor over the judge labels (`supervisor.py`).
- **E5**: judge validation and trajectory measures: a three-judge LLM panel, its agreement, and the measures built from its labels (`judge/`, `judge_measures.py`). Spec and results: `judge/DESIGN.md`.

## Running on Leonardo (CINECA)

`infra/leonardo_job.sh` is a SLURM job (one A100, 24 h) that starts a private Ollama 0.20.1 and runs the given harness command in-process (`AHI_INPROC=1`):

```bash
sbatch -J e1-gptoss infra/leonardo_job.sh harness/batch.py --exp E1 --models gpt-oss:20b --reps 3 --workers 3
```

- The Ollama binary and libraries are copied to node-local `/tmp` before starting, because GPU discovery times out (30 s) when the libraries are read from the shared filesystem.
- After `ollama serve` the script waits for a CUDA device in the log and retries up to three times. Without this check Ollama can silently run on CPU (about 14 min per judge item).
- `AHI_RUN_TMP` runs the episode on local disk (the job sets it under `/tmp`) and copies only the result files to `--out`. `AHI_VALIDATE_TMP` does the same for `validate_tasks.py` scratch copies (default `results/`).
- The paths `$WORK/ahi/{ollama,models,bin,venv,project}` and the account name inside the script are specific to the authors' project; adapt them. On the hssh swarm use `infra/Dockerfile.runner` with `submit`, not `docker run` (header of `infra/ahi-entry.sh`).

## Not in this repository

- `results/raw/`: raw episodes (Claude Code transcripts, diffs, work trees). Large, and they contain full agent output.
- `judge/items/` and `judge/out/`: judge items and outputs. They are gitignored. The item manifest maps opaque ids back to run, model and condition, and the private `id_key` makes the ids reproducible; publishing them would unblind the judging.
- Model weights (Ollama models), the Claude Code binary and the Leonardo environment.

Without these, `judge_measures.py` and `supervisor.py` cannot be re-run from a fresh clone; `aggregate.py` and `analyze.py` work from the committed CSVs.

## Citation / report

Course report for *AI-Human Interaction*, UniTo. Please cite the report; a reference will be added here.

## License

To be chosen.
