"""Human-vs-judge agreement for E5: Cohen's kappa per field with bootstrap CI (spec: judge/DESIGN.md).

  python3 judge/kappa.py --human annotations_v1.csv --judge judge/out/annot_v1.jsonl \
      --manifest judge/items/annot_v1_manifest.json

Writes results/analysis/tables/e5_kappa.csv (one row per field x model subset) and prints confusion
matrices (rows = human, columns = judge). Stdlib only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["label", "recall", "claims_complete", "main_accomplishment"]


def kappa(pairs: list) -> float:
    """Cohen's kappa for [(human, judge)]; nan when chance agreement is 1 (a single label everywhere)."""
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[x] * cb[x] for x in ca) / n ** 2
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def bootstrap_ci(pairs: list, n_boot: int = 2000, seed: int = 20261113) -> tuple:
    rng = random.Random(seed)
    ks = sorted(k for k in (kappa(rng.choices(pairs, k=len(pairs))) for _ in range(n_boot))
                if not math.isnan(k))
    return (ks[int(0.025 * len(ks))], ks[min(int(0.975 * len(ks)), len(ks) - 1)]) if ks else (math.nan,) * 2


def load(human: Path, judge: Path) -> tuple:
    h = {r["id"]: r for r in csv.DictReader(human.open())}
    j = {}
    for line in judge.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            j[r["id"]] = r  # the last line for an id wins
    return h, {i: r for i, r in j.items() if "error" not in r}


def confusion(pairs: list) -> str:
    labs = sorted({x for p in pairs for x in p})
    c = Counter(pairs)
    w = max(len(x) for x in labs) + 2
    return "\n".join([" " * w + "".join(x.rjust(w) for x in labs)] +
                     [a.ljust(w) + "".join(str(c[(a, b)]).rjust(w) for b in labs) for a in labs])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--human", required=True)
    ap.add_argument("--judge", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", default=str(ROOT / "results" / "analysis" / "tables" / "e5_kappa.csv"))
    args = ap.parse_args(argv)
    human, judge = load(Path(args.human), Path(args.judge))
    manifest = json.loads(Path(args.manifest).read_text())
    rows = []
    for field in FIELDS:
        both = [i for i in human if i in judge and i in manifest
                and (human[i].get(field) or "").strip() and judge[i].get(field)]
        for model in ["all"] + sorted({manifest[i]["model"] for i in both}):
            pairs = [(human[i][field].strip(), judge[i][field]) for i in both
                     if model == "all" or manifest[i]["model"] == model]
            if not pairs:
                continue
            lo, hi = bootstrap_ci(pairs)
            rows.append({"field": field, "model": model, "n": len(pairs),
                         "agreement": round(sum(a == b for a, b in pairs) / len(pairs), 3),
                         "kappa": round(kappa(pairs), 3), "ci_lo": round(lo, 3), "ci_hi": round(hi, 3)})
            print(f"\n{field} [{model}] n={len(pairs)} kappa={rows[-1]['kappa']} "
                  f"CI=({rows[-1]['ci_lo']}, {rows[-1]['ci_hi']})\n{confusion(pairs)}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["field", "model", "n", "agreement", "kappa", "ci_lo", "ci_hi"])
        w.writeheader()
        w.writerows(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
