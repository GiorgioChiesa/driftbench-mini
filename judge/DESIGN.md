# E5 — judge validation: design

Validate an LLM judge (`gpt-oss:120b`, served by Ollama 0.20.1) against one human annotator before
using it for the trajectory-level measures (effort share, goal recall, goal replacement, report
fidelity). Success criterion: Cohen's kappa >= 0.6 on the segment label and on `claims_complete`.

The codebook (`CODEBOOK.md`) is the single source of truth: the judge receives its sections verbatim
and the annotation page shows the same text. Frozen as v1 before the judge sees the annotation set.

## Annotation set (`annot_v1`)

From E1 only, both models, six groups: `none` k=0 and k=4 of `user`, `env`, `text`, `cascade`,
`filler`. Per model x group: 5 segments from 5 different random episodes (segment position random
among seg0, slot1-4, final) and 2 episodes for the probe/summary labels. Total 60 segment items and
24 episode items, shuffled, seed 20261113. Estimated annotation time: 2-3 h.

Both annotator and judge see the same information: the task card (goal, files the goal may change,
injected sub-tasks with source and legitimacy), the message that opened the segment, and the rendered
segment (or the probe answer and final summary). Neither sees model, k, outcomes or the other's labels.
Item ids are opaque hashes; the manifest mapping ids to runs stays private until scoring.

Cascade resolution (did the agent repair the planted breakage?) is measured deterministically from the
final repository, not by the judge.

## Files (`experiments/judge/`)

| File | Role |
|---|---|
| `CODEBOOK.md` | labels and definitions (written) |
| `build_items.py` | renders episodes into items; modes `sample`, `dev` (6 items outside the sample), `all --exp E1 E2` |
| `judge.py` | calls Ollama `/api/chat`, codebook section as instructions, JSON-schema output, `think: medium`, temperature 0, resumable |
| `make_html.py` | self-contained `annotate_v1.html`: codebook, one card per item, radio buttons, notes, localStorage autosave, CSV export |
| `kappa.py` | Cohen's kappa per field with bootstrap CI, confusion matrices, by model; `results/analysis/tables/e5_kappa.csv` |

## Item rendering

- Segment: assistant text (`AGENT:`), tool calls (`TOOL Bash/Read/Edit/Write` with inputs truncated:
  command 400, Write 700, Edit old 350/new 600 chars), tool results (`RESULT:` 400 chars), and
  `[segment ended: turn limit reached]`. Capped at 14k characters, keeping head and tail.
- Opening message: the goal (seg0), the user side request, the filler text, "Please continue." or the
  FINAL prompt, reconstructed from `spec.json` and the harness constants.
- Episode: probe answer (`probe_text`) and final summary (`final_text`, or "(no final segment)").

## Procedure

1. Build `annot_v1` and `dev` on Leonardo.
2. Run the judge on `dev` (6 items, not annotated) only to check that the pipeline and JSON output
   work. No prompt tuning on the annotation set.
3. Run the judge on `annot_v1` (SLURM, 2 x A100: `sbatch --gres=gpu:2 ... infra/leonardo_job.sh judge/judge.py judge/items/annot_v1.jsonl`).
4. The human annotates `annotate_v1.html` and exports the CSV.
5. `kappa.py`. If kappa >= 0.6: run the judge on `all_E1_E2`. Otherwise analyse disagreements, write
   codebook v2, and validate it on a fresh sample.
