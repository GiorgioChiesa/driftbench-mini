import json
import sys

import pytest

from conftest import ROOT, write_episode

sys.path.insert(0, str(ROOT / "harness"))
import run_episode as re_  # noqa: E402
import build_items as bi  # noqa: E402

ARGS = ["--task", "T01_invoice", "--model", "m-a", "--source", "user", "--k", "4", "--exp", "E3"]


class Stop(Exception):
    pass


def run_until_probe(monkeypatch, tmp_path, extra):
    calls = []

    def fake(run_dir, tag, model, message, turns, session, *a, **kw):
        calls.append((tag, message))
        if tag == "probe":
            raise Stop
        return {"tag": tag, "session_id": "sid"}

    monkeypatch.setattr(re_, "run_claude", fake)
    with pytest.raises(Stop):
        re_.main(ARGS + ["--out", str(tmp_path)] + extra)
    return calls


@pytest.mark.parametrize("n", ["-1", str(re_.N_SLOTS + 1)])
def test_compact_after_out_of_range_is_rejected(n, tmp_path):
    with pytest.raises(SystemExit):
        re_.main(ARGS + ["--out", str(tmp_path), "--compact-after", n])


def test_compact_runs_right_after_the_chosen_slot(monkeypatch, tmp_path):
    calls = run_until_probe(monkeypatch, tmp_path, ["--compact-after", "2"])
    assert [t for t, _ in calls] == ["seg0", "slot1", "slot2", "compact", "slot3", "slot4", "final", "probe"]
    assert dict(calls)["compact"] == "/compact"
    spec = json.loads((tmp_path / "E3_T01_invoice_m-a_user4_compact2_r0" / "spec.json").read_text())
    assert spec["compact_after"] == 2 and spec["condition"] == "none"


def test_no_compact_by_default(monkeypatch, tmp_path):
    calls = run_until_probe(monkeypatch, tmp_path, [])
    assert "compact" not in [t for t, _ in calls]
    assert (tmp_path / "E3_T01_invoice_m-a_user4_none_r0").exists()


def test_build_items_skips_compact_segment(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    d = write_episode(raw, "E3", "m-a", "user", 4, 0)
    (d / "compact.jsonl").write_text(
        '{"type": "assistant", "message": {"content": [{"type": "text", "text": "summary"}]}}\n')
    assert bi.segment_tags(d) == ["seg0", "slot1", "slot2", "slot3", "slot4", "final"]
    out = tmp_path / "items"
    assert bi.main(["all", "--exp", "E3", "--raw", str(raw), "--out", str(out)]) == 0
    manifest = json.loads((out / "all_E3_manifest.json").read_text())
    assert {e["segment"] for e in manifest.values()} == {
        "seg0", "slot1", "slot2", "slot3", "slot4", "final", "episode"}
