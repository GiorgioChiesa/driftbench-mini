import json
import re
from collections import Counter

import pytest

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
    assert "w" * 700 + "...[truncated]" in "\n".join(out) and "w" * 701 not in "".join(out)
    assert "  old: " + "o" * 350 + "...[truncated]" in out
    assert "  new: " + "n" * 600 + "...[truncated]" in out
    assert out[-2] == "RESULT: " + "r" * 400 + "...[truncated]"
    assert out[-1] == "[segment ended: turn limit reached]"


@pytest.mark.parametrize("block,limit", [
    ({"name": "Bash", "input": {"command": "{}"}}, 400),
    ({"name": "Write", "input": {"file_path": "a", "content": "{}"}}, 700),
    ({"name": "Edit", "input": {"file_path": "a", "old_string": "{}", "new_string": ""}}, 350),
    ({"name": "Edit", "input": {"file_path": "a", "old_string": "", "new_string": "{}"}}, 600),
])
def test_truncation_boundary(tmp_path, block, limit):
    """Exactly `limit` chars pass untouched, one more is cut (limits are literals from the spec)."""
    def render(n):
        b = json.loads(json.dumps(block).replace("{}", "x" * n))
        p = tmp_path / f"s{n}.jsonl"
        p.write_text(ev_assistant(dict(b, type="tool_use")))
        return bi.render_segment(p)
    assert "truncated" not in render(limit) and "x" * limit in render(limit)
    assert render(limit + 1).count("x") == limit and "...[truncated]" in render(limit + 1)


def test_other_tool_input_is_cut_at_400_chars_of_json(tmp_path):
    for n, cut in ((391, False), (392, True)):  # '{"p": "' + n + '"}' is n + 9 chars
        p = tmp_path / f"t{n}.jsonl"
        p.write_text(ev_assistant({"type": "tool_use", "name": "Task", "input": {"p": "x" * n}}))
        assert ("truncated" in bi.render_segment(p)) is cut


def test_result_boundary(tmp_path):
    for n, cut in ((400, False), (401, True)):
        p = tmp_path / f"r{n}.jsonl"
        p.write_text(ev_result("r" * n))
        assert ("truncated" in bi.render_segment(p)) is cut


def test_cap_exact_head_and_tail(tmp_path):
    def render(body_len):
        body = "".join(str(i % 10) for i in range(body_len))
        p = tmp_path / f"c{body_len}.jsonl"
        p.write_text(ev_assistant({"type": "text", "text": body}))
        return "AGENT: " + body, bi.render_segment(p)
    full, text = render(14000 - 7)  # exactly 14000 chars: kept whole
    assert text == full
    full, text = render(14001 - 7 + 500)  # 14501 chars
    assert text == full[:7000] + "\n[... 501 characters omitted ...]\n" + full[-7000:]


def test_items_jsonl_has_no_manifest_fields(raw, tmp_path):
    bi.main(["sample", "--raw", str(raw), "--out", str(tmp_path)])
    lines = (tmp_path / "annot_v1.jsonl").read_text().splitlines()
    keys = {"segment": {"id", "type", "card", "opening", "text"},
            "episode": {"id", "type", "card", "probe", "final"}}
    for line in lines:
        item = json.loads(line)
        assert set(item) == keys[item["type"]]
    assert not re.search(r"E1_T01|m-a|m-b|_none_r\d|\"(run_id|model|group|source|k|exp)\"", "\n".join(lines))


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
    eps = Counter((m["model"], m["group"], m["run_id"]) for m in man.values() if m["type"] == "episode")
    assert set(eps.values()) == {1} and len(eps) == 24  # 2 distinct episodes per cell
    assert len({m["segment"] for m in man.values() if m["type"] == "segment"}) > 1  # position varies
    assert len(man) == 84  # ids unique
    assert [i["type"] for i in items[:60]] != ["segment"] * 60  # shuffled: episodes are mixed in


def test_dev_outside_sample(raw, tmp_path):
    bi.main(["sample", "--raw", str(raw), "--out", str(tmp_path)])
    bi.main(["dev", "--raw", str(raw), "--out", str(tmp_path)])
    bi.main(["dev", "--raw", str(raw), "--out", str(tmp_path / "again")])
    s = json.loads((tmp_path / "annot_v1_manifest.json").read_text())
    d = json.loads((tmp_path / "dev_manifest.json").read_text())
    assert Counter(m["type"] for m in d.values()) == {"segment": 4, "episode": 2}
    assert not {m["run_id"] for m in s.values()} & {m["run_id"] for m in d.values()}
    assert not set(s) & set(d)  # item ids too
    assert (tmp_path / "dev.jsonl").read_text() == (tmp_path / "again" / "dev.jsonl").read_text()
