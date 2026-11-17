import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "judge"))

MODELS = ["m-a", "m-b"]
GROUPS = [("none", 0)] + [(s, 4) for s in ("user", "env", "text", "cascade", "filler")]
TAGS = ("seg0", "slot1", "slot2", "slot3", "slot4", "final")


def ev_assistant(*blocks):
    return json.dumps({"type": "assistant", "message": {"content": list(blocks)}})


def ev_result(content):
    return json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": content}]}})


def write_episode(root, exp, model, source, k, rep, task="T01_invoice"):
    """Synthetic episode folder in the harness output format (spec.json, metrics.json, <tag>.jsonl)."""
    run_id = f"{exp}_{task}_{model}_{source}{k}_none_r{rep}"
    d = root / run_id
    d.mkdir(parents=True)
    ids = {"user": ["u1", "u2", "u3", "u4"], "filler": ["f1", "f2", "f3", "f4"]}.get(source, [None] * 4)
    spec = {"run_id": run_id, "exp": exp, "task": task, "model": model, "source": source, "k": k,
            "condition": "none", "file_injections": ["c1"] if source == "cascade" and k else [],
            "slot_ids": (ids[:k] + [None] * 4)[:4]}
    (d / "spec.json").write_text(json.dumps(spec))
    for tag in TAGS:
        lines = [ev_assistant({"type": "text", "text": f"plan {tag}"},
                              {"type": "tool_use", "name": "Bash", "input": {"command": "pytest -q"}}),
                 ev_result("3 passed")]
        (d / f"{tag}.jsonl").write_text("\n".join(lines) + "\n")
    m = {"spec": spec, "segments": [{"tag": t} for t in TAGS],
         "final_text": "All done.", "probe_text": "The goal was discounts."}
    (d / "metrics.json").write_text(json.dumps(m))
    return d


@pytest.fixture
def raw(tmp_path):
    root = tmp_path / "raw"
    root.mkdir()
    for model in MODELS:
        for source, k in GROUPS:
            for rep in range(8):
                write_episode(root, "E1", model, source, k, rep)
    return root
