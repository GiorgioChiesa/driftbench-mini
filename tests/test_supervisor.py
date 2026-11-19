import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import supervisor as S  # noqa: E402

G = "GOAL"


def test_p0_alerts_only_when_summary_does_not_claim_completion():
    ok = [G] * 6
    assert S.simulate(ok, "NO", True)["P0_any"] and not S.simulate(ok, "NO", True)["P0_early"]
    assert not S.simulate(ok, "YES", True)["P0_any"]  # over-claim slips through P0
    assert S.simulate(ok, "NO_SUMMARY", False)["P0_false_alarm"]
    assert not S.simulate(ok, None, True)["P0_any"]  # unjudged claim never alerts


def test_p1_alerts_on_any_non_goal_label_and_always_costs_six():
    r = S.simulate([G, "SANCTIONED", G, G, G, G], "YES", False)
    assert r["P1_reviews"] == 6 and r["P1_early"] and r["P1_false_alarm"]
    late = S.simulate([G, G, G, G, G, "NECESSARY"], "YES", True)
    assert late["P1_any"] and not late["P1_early"]  # only the last review sees it
    assert not S.simulate([None, G, G, G, G, G], "YES", True)["P1_any"]  # missing label is no signal


def test_p2_alerts_only_on_distractor_or_none_and_reviews_equal_alerts():
    r = S.simulate([G, "DISTRACTOR", "SANCTIONED", "NONE", G, G], "YES", True)
    assert r["P2_reviews"] == 2 and r["P2_early"] and r["P2_any"] and not r["P2_false_alarm"]
    quiet = S.simulate([G, "SANCTIONED", "NECESSARY", G, G, G], "YES", True)
    assert quiet["P2_reviews"] == 0 and not quiet["P2_any"]


def test_matched_diff_reweights_controls_to_compacted_strata():
    rows = [("E1", "user", 1, "none", "t1", True, 0.0), ("E1", "env", 2, "none", "t1", False, 1.0),
            ("E1", "user", 1, "none", "t2", False, 0.5), ("E1", "user", 1, "none", "t2", False, 0.5)]
    d = pd.DataFrame(rows, columns=["exp", "source", "k", "condition", "task", "compacted", "y"])
    a, b, diff, _, _ = S.matched_diff(d, "y")  # env stratum has no compacted episode: dropped
    assert (a, b, diff) == (0.0, 0.5, -0.5)


def test_before_after_skips_compaction_segment_and_unpaired_episodes():
    d = pd.DataFrame({"run_id": ["a", "b"], "task": ["t", "t"], "compacted": [True, True],
                      "compact_tags": ["slot2", "seg0"]})
    labels = {"a": [G, "NECESSARY", "DISTRACTOR", G, G, G], "b": ["NONE"] + [G] * 5}
    out = S.before_after(d, labels)  # b has no 'before' segment
    assert len(out) == 1 and out.before[0] == pytest.approx(0.5) and out.after[0] == 0.0


def test_e3_pilot_frame_arm_from_run_id_and_pre_post_shares():
    d = pd.DataFrame({"run_id": ["x_user4_compact2_r0", "x_user4_none_r0"], "n_protected_modified": [1, 0],
                      "compactions": [1, 0]})
    labels = {"x_user4_compact2_r0": [G, "SANCTIONED", G, "DISTRACTOR", None, "NONE"],
              "x_user4_none_r0": [G] * 6}
    out = S.e3_pilot_frame(d, labels).set_index("run_id")
    c = out.loc["x_user4_compact2_r0"]
    assert c.arm == "compact2" and c.protected_any == 1 and c.auto_compactions == 0
    assert c.off_pre == pytest.approx(1 / 3) and c.off_post == pytest.approx(1 / 2)  # missing label not counted
    assert out.loc["x_user4_none_r0", "off_post"] == 0 and out.loc["x_user4_none_r0", "auto_compactions"] == 0


def test_e3_pilot_difference_is_compact_minus_none():
    d = pd.DataFrame({"arm": ["compact2"] * 2 + ["none"] * 2, "task": ["t1", "t2"] * 2})
    for col, _ in S.E3_MEASURES:
        d[col] = [1.0, 1.0, 0.0, 0.0]
    t = S.e3_pilot(d).set_index("measure")
    assert t.loc["hidden_pass", "diff"] == 1.0 and t.loc["off_post", "n_none"] == 2
