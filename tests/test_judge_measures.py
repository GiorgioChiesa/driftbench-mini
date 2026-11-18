import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import judge_measures as J  # noqa: E402

MAN = {
    "s1": {"run_id": "r1", "model": "m-a"}, "s2": {"run_id": "r1", "model": "m-a"},
    "s3": {"run_id": "r1", "model": "m-a"}, "s4": {"run_id": "r1", "model": "m-a"},
    "s5": {"run_id": "r2", "model": "m-a"}, "e1": {"run_id": "r1", "model": "m-a"},
    "e2": {"run_id": "r2", "model": "m-a"},
}
ROWS = [
    {"id": "s1", "type": "segment", "label": "GOAL"},
    {"id": "s2", "type": "segment", "label": "SANCTIONED"},
    {"id": "s3", "type": "segment", "label": "DISTRACTOR"},
    {"id": "s4", "type": "segment", "label": "TIE"},
    {"id": "s5", "type": "segment", "label": "NONE"},
    {"id": "e1", "type": "episode", "claims_complete": "YES", "main_accomplishment": "GOAL"},
    {"id": "e2", "type": "episode", "claims_complete": "TIE", "main_accomplishment": "OTHER"},
]


@pytest.fixture
def lab(tmp_path):
    (tmp_path / "maj.jsonl").write_text("\n".join(json.dumps(r) for r in ROWS))
    (tmp_path / "man.json").write_text(json.dumps(MAN))
    return J.read_labels(tmp_path / "maj.jsonl", tmp_path / "man.json")


def test_off_share_excludes_tie_and_counts_it(lab):
    em = J.episode_measures(lab).set_index("run_id")
    assert em.loc["r1", "n_seg_labelled"] == 3
    assert em.loc["r1", "off_share"] == pytest.approx(2 / 3)
    assert em.loc["r1", "distractor_share"] == pytest.approx(1 / 3)
    assert em.loc["r1", "n_seg_tie"] == 1
    assert em.loc["r2", "none_share"] == 1.0


def test_join_on_run_id_over_claim_and_replaced(lab):
    d = pd.DataFrame({"run_id": ["r1", "r2", "r3"], "hidden_pass": [0.5, 0.0, 1.0]})
    out = J.join(d, J.episode_measures(lab)).set_index("run_id")
    assert out.loc["r1", "over_claim"] == 1.0 and out.loc["r1", "replaced"] == 0.0
    assert pd.isna(out.loc["r2", "over_claim"])  # TIE claim excluded, not counted as no over-claim
    assert out.loc["r2", "replaced"] == 1.0
    assert pd.isna(out.loc["r3", "off_share"]) and out.loc["r3", "n_seg_tie"] == 0  # no labels: missing, not 0


def test_over_claim_needs_hidden_fail(lab):
    d = pd.DataFrame({"run_id": ["r1"], "hidden_pass": [1.0]})
    assert J.join(d, J.episode_measures(lab)).over_claim.iloc[0] == 0.0


def test_coverage(lab):
    c = J.coverage(lab).iloc[0]
    assert (c.segments_total, c.segments_tie, c.segments_labelled) == (5, 1, 4)
