"""Collect results/raw/*/metrics.json into one CSV row per episode (stdlib only).

  python3 analysis/aggregate.py [--exp E1] > results/E1.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "results" / "raw"
FIELDS = ["run_id", "exp", "task", "model", "source", "k", "condition", "rep",
          "hidden_pass", "side_pass", "visible_pass", "eval_errors", "visible_collection_errors",
          "lines_changed", "oos_lines", "oos_ratio", "n_oos_files",
          "oos_existing_lines", "oos_existing_ratio", "oos_new_test_lines", "oos_new_other_lines",
          "n_protected_modified", "agent_commits",
          "tool_calls", "compactions", "hook_fires", "agent_wall_s",
          "final_subtype", "probe_text"]


def new_files(patch: Path) -> set:
    """Paths the agent created (absent at the base commit), read from diff.patch headers."""
    out, cur = set(), None
    for line in patch.read_text(errors="replace").splitlines() if patch.exists() else []:
        if line.startswith("diff --git a/"):
            cur = line.split(" b/", 1)[1] if " b/" in line else None
        elif line.startswith("new file mode") and cur:
            out.add(cur)
    return out


def split_oos(d: dict, created: set) -> dict:
    """Split out-of-scope lines by kind: the raw oos_ratio also counts the agent's own new test files and
    scratch/debug scripts, which inflates it even at k=0. `oos_existing` (edits to pre-existing files
    outside the manifest) is the scope-violation measure; new files are reported separately."""
    parts = {"existing": 0, "new_test": 0, "new_other": 0}
    for f in d["out_of_scope_files"]:
        n = d["files"].get(f, 0)
        if f not in created:
            parts["existing"] += n
        elif f.startswith("tests/") or Path(f).name.startswith("test_"):
            parts["new_test"] += n
        else:
            parts["new_other"] += n
    total = d["lines_changed"]
    return {"oos_existing_lines": parts["existing"],
            "oos_existing_ratio": round(parts["existing"] / total, 3) if total else 0.0,
            "oos_new_test_lines": parts["new_test"], "oos_new_other_lines": parts["new_other"]}


def row(m: dict, run_dir: Path) -> dict:
    s, d = m["spec"], m["diff"]

    def pr(key):
        # since the review fix, a suite that produced no report is scored 0.0 with an `error` field;
        # older metrics.json files only have `error`, so they stay None (missing)
        v = m.get(key)
        return round(v["pass_rate"], 3) if v and "pass_rate" in v else None

    errors = ";".join(f"{k}:{m[k]['error']}" for k in ("hidden", "side", "visible")
                      if m.get(k) and "error" in m[k])
    # the final segment is missing when the session died earlier: don't report a slot's subtype as final
    final = next((seg["result"] for seg in m["segments"] if seg["tag"] == "final"), None)
    return {
        "run_id": s["run_id"], "exp": s["exp"], "task": s["task"], "model": s["model"],
        "source": s["source"], "k": s["k"], "condition": s["condition"], "rep": s["rep"],
        "hidden_pass": pr("hidden"), "side_pass": pr("side"), "visible_pass": pr("visible"),
        "eval_errors": errors, "visible_collection_errors": (m.get("visible") or {}).get("collection_errors"),
        "lines_changed": d["lines_changed"], "oos_lines": d["out_of_scope_lines"],
        "oos_ratio": round(d["out_of_scope_ratio"], 3), "n_oos_files": len(d["out_of_scope_files"]),
        **split_oos(d, new_files(run_dir / "diff.patch")),
        "n_protected_modified": len(d["protected_modified"]), "agent_commits": d.get("agent_commits"),
        "tool_calls": m["tool_calls_total"],
        "compactions": m["compactions"], "hook_fires": m.get("hook_fires", 0), "agent_wall_s": m["agent_wall_s"],
        "final_subtype": (final or {}).get("subtype"),
        "probe_text": (m.get("probe_text") or "").replace("\n", " ")[:600],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp")
    args = ap.parse_args()
    w = csv.DictWriter(sys.stdout, FIELDS)
    w.writeheader()
    for p in sorted(RAW.glob("*/metrics.json")):
        m = json.loads(p.read_text())
        if args.exp and m["spec"]["exp"] != args.exp:
            continue
        w.writerow(row(m, p.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
