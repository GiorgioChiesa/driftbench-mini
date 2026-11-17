import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import judge


@pytest.fixture
def server():
    """Mock Ollama: replies are popped from `replies` ((status, content)); requests are recorded."""
    state = {"replies": [], "requests": []}

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            state["requests"].append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            status, content = state["replies"].pop(0) if state["replies"] else (200, '{"label": "GOAL"}')
            self.send_response(status)
            self.end_headers()
            self.wfile.write(json.dumps({"message": {"content": content}}).encode())

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    state["host"] = f"127.0.0.1:{srv.server_port}"
    yield state
    srv.shutdown()


def seg(i):
    return {"id": i, "type": "segment", "card": "card", "opening": "open", "text": "AGENT: hi"}


def test_codebook_sections_and_labels():
    cb = judge.codebook()
    text, fields = cb["segment"]
    assert fields == {"label": ["GOAL", "SANCTIONED", "NECESSARY", "DISTRACTOR", "NONE"]}
    assert "Choose the ONE label" in text and "claims_complete" not in text
    assert cb["episode"][1] == {"recall": ["CORRECT", "PARTIAL", "WRONG"],
                                "claims_complete": ["YES", "NO", "NO_SUMMARY"],
                                "main_accomplishment": ["GOAL", "SUBTASK", "NONE"]}


def test_request_shape_and_retry(server):
    server["replies"] = [(503, "")]
    row = judge.judge_item(seg("a"), judge.codebook(), server["host"], "gpt-oss:120b", backoff=0)
    assert row == {"id": "a", "type": "segment", "label": "GOAL"}
    req = server["requests"][-1]
    assert len(server["requests"]) == 2
    assert req["think"] == "medium" and req["options"]["temperature"] == 0 and req["stream"] is False
    assert req["format"] == {"type": "object", "additionalProperties": False, "required": ["label"],
                             "properties": {"label": {"type": "string",
                                                      "enum": ["GOAL", "SANCTIONED", "NECESSARY", "DISTRACTOR", "NONE"]}}}
    assert req["model"] == "gpt-oss:120b"
    assert req["messages"][0]["content"].startswith("## Segment label")


def test_invalid_json_is_an_error_row(server):
    server["replies"] = [(200, "not json")]
    row = judge.judge_item(seg("a"), judge.codebook(), server["host"], "m", backoff=0)
    assert "error" in row and "label" not in row


def test_episode_request_schema(server):
    server["replies"] = [(200, json.dumps({"recall": "WRONG", "claims_complete": "NO", "main_accomplishment": "NONE"}))]
    item = {"id": "e", "type": "episode", "card": "card", "probe": "my probe", "final": "my final"}
    row = judge.judge_item(item, judge.codebook(), server["host"], "m", backoff=0)
    assert row == {"id": "e", "type": "episode", "recall": "WRONG", "claims_complete": "NO",
                   "main_accomplishment": "NONE"}
    req = server["requests"][0]
    assert req["format"]["required"] == ["recall", "claims_complete", "main_accomplishment"]
    assert req["format"]["properties"]["claims_complete"]["enum"] == ["YES", "NO", "NO_SUMMARY"]
    assert "### PROBE ANSWER\nmy probe" in req["messages"][1]["content"] and "my final" in req["messages"][1]["content"]
    assert req["messages"][0]["content"].startswith("## Episode labels")


def test_label_outside_enum_is_an_error_row(server):
    server["replies"] = [(200, '{"label": "MAYBE"}')]
    row = judge.judge_item(seg("a"), judge.codebook(), server["host"], "m", backoff=0)
    assert "error" in row and "label" not in row


def test_resume_after_interrupt_has_no_duplicates(server, tmp_path, monkeypatch):
    items, out = tmp_path / "items.jsonl", tmp_path / "out.jsonl"
    items.write_text("".join(json.dumps(dict(seg(i), card=f"card-{i}")) + "\n" for i in "abcde"))
    real = judge.judge_item

    def dying(item, *a, **kw):
        if item["id"] == "c":
            raise KeyboardInterrupt
        return real(item, *a, **kw)

    monkeypatch.setattr(judge, "judge_item", dying)
    with pytest.raises(KeyboardInterrupt):
        judge.main([str(items), "--out", str(out), "--host", server["host"]])
    assert [json.loads(line)["id"] for line in out.read_text().splitlines()] == ["a", "b"]  # flushed before the crash
    monkeypatch.setattr(judge, "judge_item", real)
    server["requests"].clear()
    judge.main([str(items), "--out", str(out), "--host", server["host"]])
    assert [json.loads(line)["id"] for line in out.read_text().splitlines()] == list("abcde")
    sent = [r["messages"][1]["content"] for r in server["requests"]]
    assert len(sent) == 3 and all(f"card-{i}" in m for i, m in zip("cde", sent))


def test_resume_retries_error_rows(server, tmp_path):
    items, out = tmp_path / "items.jsonl", tmp_path / "out.jsonl"
    items.write_text(json.dumps(seg("a")) + "\n")
    out.write_text(json.dumps({"id": "a", "type": "segment", "error": "URLError: down"}) + "\n")
    judge.main([str(items), "--out", str(out), "--host", server["host"]])
    assert len(server["requests"]) == 1


def test_resume_skips_done_ids(server, tmp_path):
    items, out = tmp_path / "items.jsonl", tmp_path / "out.jsonl"
    items.write_text("".join(json.dumps(seg(i)) + "\n" for i in "abc"))
    out.write_text(json.dumps({"id": "a", "type": "segment", "label": "NONE"}) + "\n")
    judge.main([str(items), "--out", str(out), "--host", server["host"]])
    judge.main([str(items), "--out", str(out), "--host", server["host"]])  # second run: nothing left
    rows = [json.loads(line) for line in out.read_text().splitlines()]
    assert [r["id"] for r in rows] == ["a", "b", "c"] and rows[0]["label"] == "NONE"
    assert len(server["requests"]) == 2
