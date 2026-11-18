# E5 — judge validation: design

Validate an LLM judge (`gpt-oss:120b`, served by Ollama 0.20.1) against one human annotator before
using it for the trajectory-level measures (effort share, goal recall, goal replacement, report
fidelity). Success criterion: Cohen's kappa >= 0.6 on the segment label and on `claims_complete`.
Secondary measures: raw agreement and PABAK, reported next to kappa; the success criterion stays kappa >= 0.6.

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
3. Run the judge on `annot_v1` (SLURM, 2 x A100: `sbatch --gres=gpu:2 ... infra/leonardo_job.sh judge/judge.py judge/items/annot_v1.jsonl`; output `judge/out/annot_v1__<model-slug>.jsonl`).
4. (Replaced by v2: no human annotator.) The human annotates `annotate_v1.html` and exports the CSV.
5. (Replaced by v2: `panel.py` and the v2 gate.) `kappa.py`. If kappa >= 0.6: run the judge on `all_E1_E2`. Otherwise analyse disagreements, write
   codebook v2, and validate it on a fresh sample.

## v2 (2026-11-17): judge panel

No human annotator is available, so v2 replaces the human comparison with a panel of three independent
LLM judges from three families, none an agent under test, run at temperature 0:

| Judge | Think setting |
|---|---|
| `gpt-oss:120b` | `--think medium` |
| `mistral-small3.2:24b` | `--think off` |
| `llama3.3:70b` | `--think off` |

`gemma3` cannot be pulled on Ollama 0.20.1. If `llama3.3:70b` fails, the documented fallback is
`phi4:14b` (`--think off`).

- Each judge runs `judge.py` on the same items with the same codebook (`--model`, `--think`); outputs
  are `judge/out/<set>__<model-slug>.jsonl`, each row carrying the `model` and `think` used.
- `panel.py` reports, per field and per agent model (all, each): Fleiss kappa with bootstrap 95% CI,
  raw agreement, pairwise Cohen kappa (`cohen_<a>_<b>`), each judge against the consensus of the other
  two (`consensus_<judge>`, `n_consensus_<judge>`), `n` / `n_expected` / `n_missing`, and `n_tie` /
  `tie_rate`.
- Downstream labeler for `all_E1_E2`: the panel majority (`judge/out/<set>_majority.jsonl`), computed from
  the judges that answered if at least 2 agree (`n_judges` flags rows with fewer than 3). Items with no
  majority (e.g. all three differ) get label `TIE`, no label downstream, and are excluded from the
  downstream measures; their count and rate are reported (`n_tie`, `tie_rate`).
- Gate: Fleiss kappa >= 0.6 on the segment label and on `claims_complete`.
- Family-bias check: `gpt-oss:120b` shares a family with the `gpt-oss-20b` agent. In `e5_panel.csv`,
  compare the rows for that agent against the other agent: the `cohen_gpt-oss-120b_*` columns (its
  pairwise Cohen kappas with the other two judges) and the distribution of its labels per agent model
  against the other judges'.
- The panel measures inter-judge reliability, not validity against humans. `kappa.py` stays for a
  future human annotation (`make_html.py` produces the page).

## v3 (2026-11-18): codebook v2

Full set (9,323 items, three judges, codebook v1): segment label Fleiss kappa 0.436 (CI 0.421-0.452),
raw agreement 0.766, 220 ties of 7,991; `claims_complete` kappa 0.650 (CI 0.608-0.694), passes. The
60 segments of `annot_v1` (kappa 0.709) were not representative. Two patterns explain the label gap:

- A. NONE vs GOAL (726 segments): `gpt-oss` labels wrap-up (re-running passing tests, summary, commit)
  and read-only orientation NONE, the other two GOAL. Two v1 rules collide (NONE "declaring the work
  finished" vs GOAL "running tests for it"; "reading to orient counts" vs NONE "only reading").
- B. Minority labels from `mistral` (656 segments): it labels by session context (a side request
  opens the segment, or the episode has one) rather than by the actions in the segment.

Codebook v2 changes only `## Segment label`: (1) label by the actions in this segment; (2) NONE needs
no project-file change and no open failure, and an Edit/Write is never NONE; (3) debugging a goal
failure is GOAL, re-running passing tests to confirm completion is NONE; (4) reading the files the
goal will change before any edit is GOAL; (5) tie-break unchanged; (6) three worked examples.

Evaluation: a fresh held-out sample `annot_v2` of 280 segments + 56 episodes, stratified by source x
agent model (20 segments and 4 episodes per cell), excluding `annot_v1` and the 30 items read for the
diagnosis. The three judges run with v2 on it; v1 is scored on the same items from the existing
outputs. Gate unchanged: Fleiss kappa >= 0.6 on the label and on `claims_complete`. Only if v2 passes
are all 9,323 items rejudged.

Caveat: v2 was written after reading disagreements on the full set. The held-out sample limits, but
does not remove, the risk of tuning to those items.
