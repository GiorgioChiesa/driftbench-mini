"""Run a grid of episodes with a few parallel workers (resumable: finished runs are skipped).

  python3 harness/batch.py --exp E0 --models qwen3-coder:30b gpt-oss:20b --workers 2
  python3 harness/batch.py --exp E1 --models qwen3-coder:30b --reps 3 --workers 3
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASKS = HERE.parent / "driftbench" / "tasks"

# (source, k, condition) cells per experiment
GRIDS = {
    "E0": [("none", 0, "none"), ("mix", 4, "none")],
    "E1": [("none", 0, "none")]
          + [(src, k, "none") for src in ("user", "env", "text", "cascade", "filler") for k in (1, 2, 4)],
    # mitigations at the heaviest load: one sub-task of every source (mix), 4 slots
    "E2": [("mix", 4, c) for c in ("none", "anchor", "checklist", "subagent", "tasklist")],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True, choices=sorted(GRIDS))
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    tasks = args.tasks or sorted(p.name for p in TASKS.iterdir() if (p / "task.json").exists())
    jobs = [(m, t, s, k, c, r) for r in range(args.reps) for m in args.models for t in tasks
            for (s, k, c) in GRIDS[args.exp]]
    print(f"{len(jobs)} episodes, {args.workers} workers", flush=True)

    def run(job):
        m, t, s, k, c, r = job
        cmd = [sys.executable, str(HERE / "run_episode.py"), "--exp", args.exp, "--model", m, "--task", t,
               "--source", s, "--k", str(k), "--condition", c, "--rep", str(r)]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        tail = (proc.stdout.strip().splitlines() or [""])[-1] if proc.returncode == 0 else proc.stderr[-500:]
        print(f"[{time.strftime('%H:%M:%S')}] {time.time() - t0:6.0f}s rc={proc.returncode} {tail}", flush=True)

    with ThreadPoolExecutor(args.workers) as pool:
        list(pool.map(run, jobs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
