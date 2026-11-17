import csv
import json

import pytest

import kappa


def test_kappa_hand_computed():
    # 10 items: both say GOAL 5x, both NONE 3x, human GOAL/judge NONE 1x, human NONE/judge GOAL 1x.
    # po = 0.8; human marginals GOAL .6 NONE .4, judge GOAL .6 NONE .4 -> pe = .36 + .16 = .52
    # kappa = (.8 - .52) / (1 - .52) = 0.58333...
    pairs = [("GOAL", "GOAL")] * 5 + [("NONE", "NONE")] * 3 + [("GOAL", "NONE"), ("NONE", "GOAL")]
    assert kappa.kappa(pairs) == pytest.approx(0.28 / 0.48)
    lo, hi = kappa.bootstrap_ci(pairs)
    assert lo < 0.5833 < hi and kappa.bootstrap_ci(pairs) == (lo, hi)  # seeded
    assert kappa.kappa([("A", "A")] * 4) != kappa.kappa([("A", "A")] * 4)  # nan: no variation


def test_kappa_asymmetric_marginals():
    # human GOAL 6 NONE 4; judge GOAL 4 NONE 6; po = 0.6; pe = .6*.4 + .4*.6 = 0.48; kappa = .12/.52
    pairs = [("GOAL", "GOAL")] * 3 + [("GOAL", "NONE")] * 3 + [("NONE", "GOAL")] + [("NONE", "NONE")] * 3
    assert kappa.kappa(pairs) == pytest.approx(0.12 / 0.52)


def test_cli_writes_table_split_by_model(tmp_path, capsys):
    ids = [f"i{n}" for n in range(10)]
    human = tmp_path / "h.csv"
    with human.open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["id", "label", "recall", "claims_complete", "main_accomplishment", "notes"])
        w.writeheader()
        for n, i in enumerate(ids):
            w.writerow({"id": i, "label": "GOAL" if n < 6 else "NONE"})
    judge = tmp_path / "j.jsonl"
    judge.write_text("".join(json.dumps({"id": i, "type": "segment", "label": "GOAL" if n < 6 else "NONE"}) + "\n"
                             for n, i in enumerate(ids)))
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({i: {"model": "a" if n % 2 else "b"} for n, i in enumerate(ids)}))
    out = tmp_path / "tables" / "e5_kappa.csv"
    kappa.main(["--human", str(human), "--judge", str(judge), "--manifest", str(manifest), "--out", str(out)])
    rows = list(csv.DictReader(out.open()))
    assert [(r["field"], r["model"], r["n"], r["kappa"]) for r in rows] == [
        ("label", "all", "10", "1.0"), ("label", "a", "5", "1.0"), ("label", "b", "5", "1.0")]
    assert "GOAL" in capsys.readouterr().out
