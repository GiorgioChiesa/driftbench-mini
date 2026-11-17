import csv
import json

import pytest

import judge
import panel
from test_judge import seg, server  # noqa: F401  (server is a fixture)


def test_think_payload_per_model(server):
    cb = judge.codebook()
    for model, think, expect in [("gpt-oss:120b", "auto", "medium"), ("gemma3:27b", "auto", None),
                                 ("mistral-small3.2:24b", "auto", None), ("gpt-oss:120b", "none", None),
                                 ("gemma3:27b", "high", "high"), ("gpt-oss:120b", "low", "low")]:
        judge.judge_item(seg("a"), cb, server["host"], model, think, backoff=0)
        req = server["requests"][-1]
        assert req.get("think") == expect and ("think" in req) == (expect is not None)
        assert req["model"] == model and req["options"]["temperature"] == 0


def test_default_out_has_model_slug(server, tmp_path, monkeypatch):
    monkeypatch.setattr(judge, "HERE", tmp_path)
    items = tmp_path / "annot_v1.jsonl"
    items.write_text(json.dumps(seg("a")) + "\n")
    for model in ("gemma3:27b", "mistral-small3.2:24b"):
        judge.main([str(items), "--model", model, "--host", server["host"]])
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == [
        "annot_v1__gemma3-27b.jsonl", "annot_v1__mistral-small3.2-24b.jsonl"]


def test_fleiss_hand_computed():
    # items AAA AAA BBB AAB, 3 judges: P_i = 1, 1, 1, 1/3 -> Pbar = 5/6; p_A = 8/12 -> pe = 5/9
    # kappa = (5/6 - 5/9) / (1 - 5/9) = 0.625; mean pairwise agreement = Pbar
    rows = [tuple("AAA"), tuple("AAA"), tuple("BBB"), tuple("AAB")]
    assert panel.fleiss(rows) == pytest.approx(0.625)
    assert panel.agreement(rows) == pytest.approx(5 / 6)
    assert [panel.majority(list(r)) for r in rows] == ["A", "A", "B", "A"]
    assert panel.majority(["A", "B", "C"]) == "TIE" and panel.majority(["A", "B"]) == "TIE"


def test_panel_cli(tmp_path):
    labels = {"j1": "GOAL GOAL NONE GOAL", "j2": "GOAL GOAL NONE GOAL", "j3": "GOAL GOAL NONE NONE"}
    files = []
    for name, labs in labels.items():
        f = tmp_path / f"set__{name}.jsonl"
        f.write_text("".join(json.dumps({"id": f"i{n}", "type": "segment", "label": lab}) + "\n"
                             for n, lab in enumerate(labs.split())))
        files.append(str(f))
    man = tmp_path / "set_manifest.json"
    man.write_text(json.dumps({f"i{n}": {"type": "segment", "model": "a" if n < 2 else "b"} for n in range(5)}))
    out, maj = tmp_path / "t" / "e5_panel.csv", tmp_path / "maj.jsonl"
    panel.main(["--judges", *files, "--manifest", str(man), "--out", str(out), "--majority-out", str(maj)])
    rows = {r["model"]: r for r in csv.DictReader(out.open())}
    assert list(rows) == ["all", "a", "b"]
    r = rows["all"]  # i4 has no judge label: missing
    assert (r["n"], r["n_expected"], r["n_missing"], r["n_tie"]) == ("4", "5", "1", "0")
    assert float(r["fleiss"]) == pytest.approx(0.625, abs=1e-3) and float(r["agreement"]) == pytest.approx(0.833, abs=1e-3)
    assert float(r["cohen_j1_j2"]) == 1.0 and "loo_j3" in r and r["fleiss_lo"] and r["fleiss_hi"]
    assert [json.loads(line)["label"] for line in maj.read_text().splitlines()] == ["GOAL", "GOAL", "NONE", "GOAL"]
