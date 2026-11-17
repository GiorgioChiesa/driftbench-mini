import json
from collections import Counter

import build_items as bi
from conftest import ev_assistant, ev_result


def test_render_truncates_and_marks_turn_limit(tmp_path):
    p = tmp_path / "s.jsonl"
    lines = [
        ev_assistant({"type": "text", "text": "hello"},
                     {"type": "tool_use", "name": "Bash", "input": {"command": "x" * 500}},
                     {"type": "tool_use", "name": "Write", "input": {"file_path": "a.py", "content": "w" * 800}},
                     {"type": "tool_use", "name": "Edit", "input": {
                         "file_path": "b.py", "old_string": "o" * 400, "new_string": "n" * 700}}),
        ev_result([{"type": "text", "text": "r" * 500}]),
        json.dumps({"type": "result", "subtype": "error_max_turns"}),
    ]
    p.write_text("\n".join(lines))
    out = bi.render_segment(p).splitlines()
    assert out[0] == "AGENT: hello"
    assert out[1] == "TOOL Bash: " + "x" * 400 + "...[truncated]"
    assert "w" * 700 + "...[truncated]" in out[2:4][1] and "w" * 701 not in "".join(out)
    assert "  old: " + "o" * 350 + "...[truncated]" in out
    assert "  new: " + "n" * 600 + "...[truncated]" in out
    assert out[-2] == "RESULT: " + "r" * 400 + "...[truncated]"
    assert out[-1] == "[segment ended: turn limit reached]"


def test_cap_keeps_head_and_tail(tmp_path):
    p = tmp_path / "s.jsonl"
    p.write_text("\n".join(ev_assistant({"type": "text", "text": f"{c}" * 5000}) for c in "abcd"))
    text = bi.render_segment(p)
    assert len(text) < 14200
    assert text.startswith("AGENT: aaa") and text.endswith("ddd") and "omitted" in text


def test_opening_and_card(raw):
    run = raw / "E1_T01_invoice_m-a_user4_none_r0"
    item, entry = bi.make_item(run, "segment", "slot2")
    assert item["opening"].startswith("One more thing")  # u2, reconstructed from task.json
    assert "[user, sanctioned] Side request" in item["card"]
    assert bi.make_item(run, "segment", "final")[0]["opening"] == bi.FINAL
    assert entry["group"] == "user4" and entry["segment"] == "slot2"
    c = bi.make_item(raw / "E1_T01_invoice_m-a_cascade4_none_r0", "segment", "seg0")[0]
    assert "[cascade, necessary] planted in invoice/money.py" in c["card"]
    f = bi.make_item(raw / "E1_T01_invoice_m-a_filler4_none_r0", "segment", "slot1")[0]
    assert f["opening"].startswith("FYI") and "(none)" in f["card"]


def test_sample_shape_and_determinism(raw, tmp_path):
    for name in ("a", "b"):
        bi.main(["sample", "--raw", str(raw), "--out", str(tmp_path / name)])
    a, b = (tmp_path / n / "annot_v1.jsonl" for n in "ab")
    assert a.read_text() == b.read_text()
    items = [json.loads(line) for line in a.read_text().splitlines()]
    assert Counter(i["type"] for i in items) == {"segment": 60, "episode": 24}
    man = json.loads((tmp_path / "a" / "annot_v1_manifest.json").read_text())
    segs = Counter((m["model"], m["group"]) for m in man.values() if m["type"] == "segment")
    assert set(segs.values()) == {5} and len(segs) == 12
    per_cell = Counter((m["model"], m["group"], m["run_id"]) for m in man.values() if m["type"] == "segment")
    assert set(per_cell.values()) == {1}  # 5 different episodes per cell


def test_dev_outside_sample(raw, tmp_path):
    bi.main(["sample", "--raw", str(raw), "--out", str(tmp_path)])
    bi.main(["dev", "--raw", str(raw), "--out", str(tmp_path)])
    s = json.loads((tmp_path / "annot_v1_manifest.json").read_text())
    d = json.loads((tmp_path / "dev_manifest.json").read_text())
    assert len(d) == 6
    assert not {m["run_id"] for m in s.values()} & {m["run_id"] for m in d.values()}
