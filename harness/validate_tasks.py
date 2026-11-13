"""Sanity checks for DriftBench-mini tasks (run on the host with the ahi-agent image built).

For every task: the untouched repo passes its visible tests and fails the hidden ones; the reference
solution passes the hidden tests; each env distractor breaks a visible test without touching the
goal; each cascade breaks the reference solution (hidden or visible); every op applies cleanly.
Before running anything, `lint` checks the task.json structure the harness relies on.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_episode import N_SLOTS, TASKS, apply_ops, run_pytest  # noqa: E402

KINDS = {"user": "sanctioned", "env": "distractor", "text": "distractor", "cascade": "necessary"}


def lint(task_dir: Path, task: dict) -> list:
    """Structural problems in task.json (empty list = fine)."""
    probs = []
    ids = set()
    for src, kind in KINDS.items():
        items = task["injections"].get(src, [])
        if len(items) != N_SLOTS:
            probs.append(f"{src}: {len(items)} items, need {N_SLOTS} (k=4 would silently run fewer)")
        for item in items:
            if item["id"] in ids:
                probs.append(f"duplicate id {item['id']}")
            ids.add(item["id"])
            if item.get("kind") != kind:
                probs.append(f"{item['id']}: kind {item.get('kind')!r}, expected {kind!r}")
            if kind == "distractor" and item.get("extend_allowed"):
                probs.append(f"{item['id']}: a distractor must not extend the allowed scope")
            if src == "user" and not (task_dir / "side_tests" / f"test_side_{item['id']}.py").exists():
                probs.append(f"{item['id']}: no side test")
            if src != "user" and not item.get("ops"):
                probs.append(f"{item['id']}: no ops")
    written = {op["file"] for src in KINDS for item in task["injections"].get(src, [])
               for op in item.get("ops", []) if op["op"] == "write"}
    for f in task["allowed"] + task["protected"]:
        if not (task_dir / "repo" / f).exists() and not (task_dir / "solution" / f).exists() \
                and f not in written:
            probs.append(f"allowed/protected path not in repo or solution: {f}")
    return probs


def build(tmp: Path, task_dir: Path, name: str, solution: bool, ops: list) -> Path:
    repo = tmp / name
    shutil.copytree(task_dir / "repo", repo)
    if solution and (task_dir / "solution").exists():
        shutil.copytree(task_dir / "solution", repo, dirs_exist_ok=True)
    apply_ops(repo, ops)
    return repo


def rate(res) -> str:
    if res is None or "pass_rate" not in res:
        return "ERR"
    return f"{res['pass_rate']:.2f}" + (f"({res['error']})" if "error" in res else "")


def check(task_dir: Path) -> list:
    task = json.loads((task_dir / "task.json").read_text())
    hidden = sorted((task_dir / "hidden_tests").glob("test_*.py"))
    rows = [("LINT", "task.json", "FAIL", p) for p in lint(task_dir, task)]
    # AHI_VALIDATE_TMP: scratch dir for the copies (default results/; a local disk avoids GlusterFS stalls)
    tmp_root = os.environ.get("AHI_VALIDATE_TMP", str(task_dir.parent.parent.parent / "results"))
    with tempfile.TemporaryDirectory(dir=tmp_root) as t:
        tmp = Path(t)

        def run(name, solution, ops, tests):
            repo = build(tmp, task_dir, name, solution, ops)
            return run_pytest(tmp, repo, tests, name)

        rows.append(("base", "visible", rate(run("base_v", False, [], [])), "expect 1.00"))
        rows.append(("base", "hidden", rate(run("base_h", False, [], hidden)), "expect <1"))
        rows.append(("solution", "hidden", rate(run("sol_h", True, [], hidden)), "expect 1.00"))
        rows.append(("solution", "visible", rate(run("sol_v", True, [], [])), "expect 1.00"))
        inj = task["injections"]
        for item in inj["env"]:
            rows.append((item["id"], "visible", rate(run(item["id"] + "_v", True, item["ops"], [])), "expect <1"))
        for item in inj["text"]:
            rows.append((item["id"], "hidden", rate(run(item["id"] + "_h", True, item["ops"], hidden)), "expect 1.00"))
        for item in inj["cascade"]:
            h = rate(run(item["id"] + "_h", True, item["ops"], hidden))
            v = rate(run(item["id"] + "_v", True, item["ops"], []))
            rows.append((item["id"], "hid/vis", f"{h}/{v}", "expect one <1"))
        for item in inj["user"]:
            side = task_dir / "side_tests" / f"test_side_{item['id']}.py"
            rows.append((item["id"], "side", rate(run(item["id"] + "_s", True, [], [side])), "expect <1"))
    return rows


def main() -> int:
    names = sys.argv[1:] or sorted(p.name for p in TASKS.iterdir() if (p / "task.json").exists())
    for name in names:
        print(f"== {name}")
        for row in check(TASKS / name):
            print("  {:<10} {:<8} {:<10} {}".format(*row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
