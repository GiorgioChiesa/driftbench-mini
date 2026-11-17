import json

import pytest

import build_items as bi
from conftest import ev_assistant, ev_result, write_episode

KEY = b"test-key"


def abs_path_episode(raw):
    """A none0 run whose transcript, probe and summary contain absolute run paths."""
    d = raw / "E1_T01_invoice_m-a_none0_none_r0"
    rid = d.name
    p = f"/tmp/ahi-123/runs/{rid}/work"
    (d / "seg0.jsonl").write_text("\n".join([
        ev_assistant({"type": "tool_use", "name": "Read", "input": {"file_path": f"{p}/invoice/pricing.py"}}),
        ev_result(f"rootdir: /tmp/ahi-runs/{rid}/work\nTraceback File \"{p}/x.py\", line 3")]))
    m = json.loads((d / "metrics.json").read_text())
    m["probe_text"], m["final_text"] = f"I edited {p}/a.py", f"done in /tmp/ahi-runs/{rid}/work"
    (d / "metrics.json").write_text(json.dumps(m))
    return d, rid


def test_absolute_run_paths_are_normalised(raw):
    d, rid = abs_path_episode(raw)
    seg = bi.make_item(d, "segment", "seg0", KEY)[0]
    ep = bi.make_item(d, "episode", "", KEY)[0]
    assert "TOOL Read: /work/invoice/pricing.py" in seg["text"] and "rootdir: /work" in seg["text"]
    assert ep["probe"] == "I edited /work/a.py" and ep["final"] == "done in /work"
    blob = json.dumps([seg, ep])
    assert rid not in blob and "/tmp/ahi" not in blob


def test_leak_check_fails_on_leftover_metadata(raw):
    d, _ = abs_path_episode(raw)
    m = json.loads((d / "metrics.json").read_text())
    m["final_text"] = "ran m-a with cascade4 settings"  # not a path: scrub cannot fix it
    (d / "metrics.json").write_text(json.dumps(m))
    ep, entry = bi.make_item(d, "episode", "", KEY)
    with pytest.raises(SystemExit, match="leak check"):
        bi.check_leaks([ep], {ep["id"]: entry})


def test_ids_depend_on_key_and_are_stable(raw):
    d = raw / "E1_T01_invoice_m-a_none0_none_r0"
    a = bi.make_item(d, "segment", "seg0", KEY)[0]["id"]
    assert a == bi.make_item(d, "segment", "seg0", KEY)[0]["id"]
    assert a != bi.make_item(d, "segment", "seg0", b"other")[0]["id"]


def test_all_mode_keeps_e2_conditions(raw, tmp_path):
    d = write_episode(raw, "E2", "m-a", "none", 0, 0)
    spec = json.loads((d / "spec.json").read_text())
    spec["condition"] = "anchor"
    (d / "spec.json").write_text(json.dumps(spec))
    bi.main(["all", "--raw", str(raw), "--out", str(tmp_path), "--exp", "E2"])
    man = json.loads((tmp_path / "all_E2_manifest.json").read_text())
    assert {m["run_id"] for m in man.values()} == {spec["run_id"]}


def test_empty_run_is_skipped_so_cell_keeps_five(raw, tmp_path):
    for p in raw.glob("E1_T01_invoice_m-a_env4_none_r*"):  # make 3 of 8 runs empty
        if p.name.endswith(("r0", "r1", "r2")):
            for f in p.glob("*.jsonl"):
                f.write_text("")
    bi.main(["sample", "--raw", str(raw), "--out", str(tmp_path)])
    man = json.loads((tmp_path / "annot_v1_manifest.json").read_text())
    n = sum(m["type"] == "segment" and m["model"] == "m-a" and m["group"] == "env4" for m in man.values())
    assert n == 5
