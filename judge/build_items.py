"""Render raw episodes into E5 judge/annotation items (spec: judge/DESIGN.md).

  python3 judge/build_items.py sample            # annot_v1: 60 segment + 24 episode items
  python3 judge/build_items.py dev               # 6 items outside the sample
  python3 judge/build_items.py all --exp E1 E2   # every segment and episode

Writes <out>/<set>.jsonl (items, safe to show) and <out>/<set>_manifest.json (id -> run, model, k,
group, segment; private until scoring). Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import random
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from harness.run_episode import FINAL, TASKS, select_injections  # noqa: E402

SEED = 20261113
TAGS = ["seg0", "slot1", "slot2", "slot3", "slot4", "final"]
SOURCES = ["user", "env", "text", "cascade", "filler"]
CAP = 14000
LIM = {"command": 400, "write": 700, "edit_old": 350, "edit_new": 600, "result": 400}


def cut(s: str, n: int) -> str:
    s = s or ""
    return s if len(s) <= n else s[:n] + "...[truncated]"


# --------------------------------------------------------------------------- rendering
def render_tool(block: dict) -> str:
    name, inp = block.get("name", "?"), block.get("input", {}) or {}
    if name == "Bash":
        return f"TOOL Bash: {cut(inp.get('command', ''), LIM['command'])}"
    if name == "Write":
        return f"TOOL Write {inp.get('file_path', '')}:\n{cut(inp.get('content', ''), LIM['write'])}"
    if name == "Edit":
        return (f"TOOL Edit {inp.get('file_path', '')}:\n  old: {cut(inp.get('old_string', ''), LIM['edit_old'])}"
                f"\n  new: {cut(inp.get('new_string', ''), LIM['edit_new'])}")
    if name == "Read":
        return f"TOOL Read: {inp.get('file_path', '')}"
    return f"TOOL {name}: {cut(json.dumps(inp), LIM['command'])}"  # e.g. Task (sub-agent)


def render_result(block: dict) -> str:
    c = block.get("content", "")
    if isinstance(c, list):
        c = "\n".join(b.get("text", "") for b in c if isinstance(b, dict))
    return f"RESULT: {cut(str(c), LIM['result'])}"


def render_segment(path: Path) -> str:
    out, limit = [], False
    for line in path.read_text(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        content = ev.get("message", {}).get("content", [])
        if t in ("assistant", "user") and isinstance(content, list):
            for b in content:
                if t == "assistant" and b.get("type") == "text":
                    out.append(f"AGENT: {b['text']}")
                elif t == "assistant" and b.get("type") == "tool_use":
                    out.append(render_tool(b))
                elif t == "user" and b.get("type") == "tool_result":
                    out.append(render_result(b))
        elif t == "result" and ev.get("subtype") == "error_max_turns":
            limit = True
    if not out:
        return ""
    if limit:
        out.append("[segment ended: turn limit reached]")
    text = "\n".join(out)
    if len(text) > CAP:
        half = CAP // 2
        text = text[:half] + f"\n[... {len(text) - 2 * half} characters omitted ...]\n" + text[-half:]
    return text


def task_card(task_dir: Path, spec: dict) -> tuple:
    """(card text, task dict). Lists only what was injected into this session."""
    task = json.loads((task_dir / "task.json").read_text())
    known = {i["id"]: (src, i) for src, items in task["injections"].items() for i in items}
    ids = list(spec.get("file_injections") or []) + [i for i in spec.get("slot_ids") or [] if i]
    lines = []
    for i in ids:
        if i not in known:  # filler ids (f1..): no sub-task
            continue
        src, item = known[i]
        if src == "user":
            desc = item["text"]
        else:
            desc = "planted in " + "; ".join(
                f"{o['file']}: " + cut(f"{o['old'].strip()} -> {o['new'].strip()}" if o["op"] == "replace"
                                       else o["text"].strip(), 300) for o in item["ops"])
        lines.append(f"- [{src}, {item['kind']}] {desc}")
    card = ("ORIGINAL GOAL:\n" + (task_dir / "goal.md").read_text().strip()
            + "\n\nFILES THE GOAL MAY CHANGE:\n" + "\n".join(f"- {f}" for f in task["allowed"])
            + "\n\nINJECTED SUB-TASKS (source, legitimacy):\n" + ("\n".join(lines) or "(none)"))
    return card, task


def opening_message(tag: str, task_dir: Path, task: dict, spec: dict) -> str:
    if tag == "seg0":
        return (task_dir / "goal.md").read_text().strip()
    if tag == "final":
        return FINAL
    return select_injections(task, spec["source"], spec["k"])[1][int(tag[4:]) - 1]


def item_id(key: bytes, run_id: str, segment: str) -> str:
    return hmac.new(key, f"{run_id}|{segment}".encode(), hashlib.sha256).hexdigest()[:10]


# run_id = <exp>_<task>_<model>_<source><k>_<condition>_r<rep> (harness/run_episode.py)
RUN = r"E\d+_T\d+_[\w.-]+?_r\d+(?!\d)"
HOSTS = [  # absolute host prefixes that could point at the machine, and so at the model
    (r"/leonardo_(?:work|scratch(?:/fast)?)/[\w.-]+", "/host"),
    (r"/tmp/ahi[\w.-]*(?:/runs)?", "/tmp/run"),
    (r"(?<![\w./:-])/(?:home|Users)/[\w.-]+", "/home/user"),
    (r"(?<![\w./-])[\w./-]*/\.?venv/", "/venv/"),
]


def scrub(s: str) -> str:
    """Absolute run paths (`/tmp/ahi-x/runs/<run_id>/work/...`) and any run id (also sibling runs seen
    via `ls ..`) would reveal model, group, k and rep; host prefixes hint at the machine."""
    s = re.sub(rf"(?<![\w./-])[\w./-]*{RUN}/work", "/work", s)
    s = re.sub(RUN, "<run>", s)
    for pat, neutral in HOSTS:
        s = re.sub(pat, neutral, s)
    return s


def make_item(run: Path, kind: str, tag: str, key: bytes) -> tuple:
    """Return (item, manifest entry) for a segment (`tag`) or the probe/summary of episode `run`."""
    spec = json.loads((run / "spec.json").read_text())
    task_dir = TASKS / spec["task"]
    card, task = task_card(task_dir, spec)
    seg = tag if kind == "segment" else "episode"
    item = {"id": item_id(key, spec["run_id"], seg), "type": kind, "card": card}
    if kind == "segment":
        item["opening"] = opening_message(tag, task_dir, task, spec)
        item["text"] = render_segment(run / f"{tag}.jsonl")
    else:
        m = json.loads((run / "metrics.json").read_text())
        has_final = any(s["tag"] == "final" for s in m["segments"])
        item["probe"] = m.get("probe_text") or "(no probe answer)"
        item["final"] = (m.get("final_text") or "(empty)") if has_final else "(no final segment)"
    item.update({f: scrub(v) for f, v in item.items() if f not in ("id", "type")})
    entry = {"run_id": spec["run_id"], "exp": spec["exp"], "model": spec["model"], "k": spec["k"],
             "source": spec["source"], "group": f"{spec['source']}{spec['k']}", "segment": seg, "type": kind}
    return item, entry


# --------------------------------------------------------------------------- selection
def load_runs(raw: Path, exps: list, only_none: bool) -> list:
    """Runs of the given experiments; `only_none` drops E2 mitigation conditions (sample and dev)."""
    runs = []
    for p in sorted(raw.glob("*/metrics.json")):
        spec = json.loads((p.parent / "spec.json").read_text())
        if spec["exp"] in exps and (not only_none or spec.get("condition", "none") == "none"):
            runs.append((p.parent, spec))
    return runs


def segment_tags(run: Path) -> list:
    return [t for t in TAGS if (run / f"{t}.jsonl").exists() and render_segment(run / f"{t}.jsonl")]


def sample_runs(runs: list, rng: random.Random, n_seg: int = 5, n_ep: int = 2) -> tuple:
    """(segment picks [(run, tag)], episode picks [run]) per model x group."""
    segs, eps = [], []
    models = sorted({s["model"] for _, s in runs})
    for model in models:
        for source, k in [("none", 0)] + [(s, 4) for s in SOURCES]:
            cell = [r for r, s in runs if s["model"] == model and s["source"] == source and s["k"] == k]
            rng.shuffle(cell)
            used, got = 0, 0
            for r in cell:  # a run without any non-empty segment is skipped, so the cell keeps n_seg
                used += 1
                tags = segment_tags(r)
                if tags:
                    segs.append((r, rng.choice(tags)))
                    got += 1
                if got == n_seg:
                    break
            rest = cell[used:] or cell
            eps += [rest[i % len(rest)] for i in range(n_ep)] if cell else []
    return segs, eps


def build(mode: str, raw: Path, exps: list) -> list:
    rng = random.Random(SEED)
    if mode == "all":
        runs = load_runs(raw, exps, only_none=False)
        picks = [(r, "segment", t) for r, _ in runs for t in segment_tags(r)]
        picks += [(r, "episode", "") for r, _ in runs]
        return picks
    runs = load_runs(raw, ["E1"], only_none=True)
    segs, eps = sample_runs(runs, rng)
    picks = [(r, "segment", t) for r, t in segs] + [(r, "episode", "") for r in eps]
    if mode == "dev":
        used = {r for r, _, _ in picks}
        rest = [r for r, _ in runs if r not in used]
        drng = random.Random(SEED + 1)
        drng.shuffle(rest)
        picks = [(r, "segment", drng.choice(segment_tags(r))) for r in rest[:4] if segment_tags(r)]
        picks += [(r, "episode", "") for r in rest[4:6]]
        return picks
    rng.shuffle(picks)
    return picks


TEXT_FIELDS = ("card", "opening", "text", "probe", "final")


def check_leaks(items: list, manifest: dict) -> None:
    """Fail if an item shows what the annotator and judge must not see: run id, model, group, temp paths.
    Searches each raw string field (JSON escaping would hide a match at the start of a line)."""
    models = {m["model"] for m in manifest.values()}
    bad = [re.escape(x) for m in models for x in (m, m.replace(":", "-").replace("/", "-"))]
    bad += ["gpt-oss", "qwen"]
    pat = re.compile(r"(?<![\w-])(?:" + "|".join(bad) + r")(?![\w-])|/tmp/ahi|" + RUN)
    leaks = [(i["id"], m.group()) for i in items for f in TEXT_FIELDS if (m := pat.search(i.get(f) or ""))]
    if leaks:
        raise SystemExit(f"leak check failed (id, match): {leaks[:5]}")
    for name, rx in (("leonardo", r"(?i)leonardo"), ("Python 3.", r"Python 3\."),
                     ("email", r"(?<![\w.+-])[\w.+-]+@[\w.-]+"),
                     # group tokens also occur in plausible agent code (`text4 = 'a b'`): warn only
                     ("group token", r"(?<![\w-])(?:none0|(?:user|env|text|cascade|filler)4)(?![\w-])")):  # soft fingerprints: warn only
        n = sum(len(re.findall(rx, i.get(f) or "")) for i in items for f in TEXT_FIELDS)
        if n:
            print(f"warning: {n} occurrence(s) of {name} in items", file=sys.stderr)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sample", "dev", "all"])
    ap.add_argument("--exp", nargs="+", default=["E1", "E2"])
    ap.add_argument("--raw", default=str(ROOT / "results" / "raw"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "items"))
    args = ap.parse_args(argv)
    picks = build(args.mode, Path(args.raw), args.exp)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    keyfile = out / "id_key"  # private, next to the manifest: ids stay deterministic across runs
    if not keyfile.exists():
        keyfile.write_text(secrets.token_hex(32))
    key = bytes.fromhex(keyfile.read_text().strip())
    items, manifest = [], {}
    for run, kind, tag in picks:
        item, entry = make_item(run, kind, tag, key)
        if item["id"] not in manifest:  # small cells can pick the same episode twice
            items.append(item)
            manifest[item["id"]] = entry
    check_leaks(items, manifest)
    name = {"sample": "annot_v1", "dev": "dev", "all": "all_" + "_".join(args.exp)}[args.mode]
    (out / f"{name}.jsonl").write_text("".join(json.dumps(i) + "\n" for i in items))
    (out / f"{name}_manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"{name}: {sum(i['type'] == 'segment' for i in items)} segment + "
          f"{sum(i['type'] == 'episode' for i in items)} episode items -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
