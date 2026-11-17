"""Inter-judge reliability of an LLM judge panel (E5 v2, spec: judge/DESIGN.md).

  python3 judge/panel.py --judges judge/out/annot_v1__gpt-oss-120b.jsonl judge/out/annot_v1__gemma3-27b.jsonl \
      judge/out/annot_v1__mistral-small3.2-24b.jsonl --manifest judge/items/annot_v1_manifest.json

Per field and agent-model subset: Fleiss kappa (bootstrap CI by item), raw agreement, pairwise Cohen
kappa, each judge vs the majority of the others, counts. Writes results/analysis/tables/e5_panel.csv and
judge/out/<set>_majority.jsonl (majority label per item; ties are "TIE" and left out of majority stats).
Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import sys
from collections import Counter
from pathlib import Path

from kappa import FIELD_TYPE, FIELDS, ROOT, bootstrap_ci, kappa, load_judge

HERE = Path(__file__).resolve().parent


def majority(labels: list) -> str:
    top = Counter(labels).most_common(2)
    return "TIE" if len(top) > 1 and top[0][1] == top[1][1] else top[0][0]


def fleiss(rows: list) -> float:
    """Fleiss' kappa for [(label of judge 1, ..., label of judge m)] per item; nan if one label only."""
    m, n = len(rows[0]), len(rows)
    counts = [Counter(r) for r in rows]
    p_bar = sum((sum(c * c for c in cnt.values()) - m) / (m * (m - 1)) for cnt in counts) / n
    tot = Counter()
    for cnt in counts:
        tot.update(cnt)
    pe = sum((v / (n * m)) ** 2 for v in tot.values())
    return math.nan if pe == 1 else (p_bar - pe) / (1 - pe)


def agreement(rows: list) -> float:
    m = len(rows[0])
    return sum(a == b for r in rows for a, b in itertools.combinations(r, 2)) / (len(rows) * m * (m - 1) / 2)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judges", nargs="+", required=True, help="2+ judge JSONL files")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", default=str(ROOT / "results" / "analysis" / "tables" / "e5_panel.csv"))
    ap.add_argument("--majority-out")
    args = ap.parse_args(argv)
    if len(args.judges) < 2:
        ap.error("need at least 2 judge files")
    names = [Path(p).stem.split("__")[-1] for p in args.judges]
    judges = [load_judge(Path(p)) for p in args.judges]
    manifest = json.loads(Path(args.manifest).read_text())
    rows, maj = [], {}
    for field in FIELDS:
        expected = {i: m for i, m in manifest.items() if m["type"] == FIELD_TYPE[field]}
        if not expected:
            continue
        full = {i: tuple(j[i][field] for j in judges) for i in expected if all(field in j.get(i, {}) for j in judges)}
        for i, labs in full.items():
            maj.setdefault(i, {"id": i, "type": FIELD_TYPE[field]})[field] = majority(list(labs))
        for model in ["all"] + sorted({m["model"] for m in expected.values()}):
            ids = [i for i in full if model == "all" or manifest[i]["model"] == model]
            n_exp = sum(model in ("all", m["model"]) for m in expected.values())
            row = {"field": field, "model": model, "n": len(ids), "n_expected": n_exp, "n_missing": n_exp - len(ids)}
            data = [full[i] for i in ids]
            if data:
                lo, hi = bootstrap_ci(data, stat=fleiss)
                row.update(fleiss=round(fleiss(data), 3), fleiss_lo=round(lo, 3), fleiss_hi=round(hi, 3),
                           agreement=round(agreement(data), 3))
                for (a, na), (b, nb) in itertools.combinations(enumerate(names), 2):
                    row[f"cohen_{na}_{nb}"] = round(kappa([(d[a], d[b]) for d in data]), 3)
                row["n_tie"] = sum(majority(list(d)) == "TIE" for d in data)  # no panel majority
                for a, na in enumerate(names):
                    mjs = [(d[a], majority([x for k, x in enumerate(d) if k != a])) for d in data]
                    pairs = [p for p in mjs if p[1] != "TIE"]  # ties among the other judges are excluded
                    row[f"loo_{na}"] = round(kappa(pairs), 3) if pairs else ""
            rows.append(row)
            print(f"{field} [{model}] n={row['n']}/{n_exp} fleiss={row.get('fleiss')} "
                  f"CI=({row.get('fleiss_lo')}, {row.get('fleiss_hi')}) agreement={row.get('agreement')}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows(rows)
    set_name = Path(args.manifest).name.replace("_manifest.json", "")
    mout = Path(args.majority_out) if args.majority_out else HERE / "out" / f"{set_name}_majority.jsonl"
    mout.parent.mkdir(parents=True, exist_ok=True)
    mout.write_text("".join(json.dumps(r) + "\n" for r in maj.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
