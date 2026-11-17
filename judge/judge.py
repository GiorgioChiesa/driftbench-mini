"""Run the E5 LLM judge over an items JSONL with Ollama (spec: judge/DESIGN.md).

  OLLAMA_HOST=localhost:11434 python3 judge/judge.py judge/items/dev.jsonl [--out judge/out/dev.jsonl]

One output line per item: {"id", "type", <labels>} or {"id", "type", "error"}. Resumable: ids already in
the output file are skipped. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTIONS = {"segment": "Segment label", "episode": "Episode labels"}


def codebook(path: Path = HERE / "CODEBOOK.md") -> dict:
    """{type: (section text verbatim, {field: [labels]})}, parsed from the codebook's `## ` sections."""
    text = path.read_text()
    out = {}
    for kind, title in SECTIONS.items():
        m = re.search(rf"^## {title}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
        body = "## " + title + "\n" + m.group(1).rstrip() + "\n"
        if kind == "segment":
            fields = {"label": re.findall(r"^- \*\*([A-Z_]+)\*\*:", body, re.M)}
        else:
            fields = {}
            for line in body.splitlines():
                if f := re.match(r"- \*\*([a-z_]+)\*\*", line):
                    fields[f.group(1)] = []
                elif lab := re.match(r"  - \*\*([A-Z_]+)\*\*:", line):
                    fields[list(fields)[-1]].append(lab.group(1))
        out[kind] = (body, fields)
    return out


def schema(fields: dict) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(fields),
            "properties": {f: {"type": "string", "enum": labels} for f, labels in fields.items()}}


def user_message(item: dict) -> str:
    parts = [("TASK CARD", item["card"])]
    if item["type"] == "segment":
        parts += [("MESSAGE THAT OPENED THE SEGMENT", item["opening"]), ("SEGMENT", item["text"])]
    else:
        parts += [("PROBE ANSWER", item["probe"]), ("FINAL SUMMARY", item["final"])]
    return "\n\n".join(f"### {h}\n{t}" for h, t in parts)


def chat(host: str, payload: dict, retries: int = 3, backoff: float = 5.0, timeout: int = 900) -> str:
    """POST /api/chat; retry transient errors (connection, timeout, HTTP 5xx). Returns message.content."""
    url = (host if "://" in host else "http://" + host).rstrip("/") + "/api/chat"
    req = urllib.request.Request(url, json.dumps(payload).encode(), {"Content-Type": "application/json"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())["message"]["content"]
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError, KeyError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code < 500:
                raise
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))


def judge_item(item: dict, cb: dict, host: str, model: str, **kw) -> dict:
    system, fields = cb[item["type"]]
    payload = {"model": model, "stream": False, "think": "medium", "format": schema(fields),
               "options": {"temperature": 0, "num_ctx": 16384},  # 14k-char items + codebook + reasoning
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user_message(item)}]}
    row = {"id": item["id"], "type": item["type"]}
    try:
        content = chat(host, payload, **kw)
        res = json.loads(content)
        for f, labels in fields.items():
            if res.get(f) not in labels:
                raise ValueError(f"bad value for {f}: {res.get(f)!r}")
        row.update({f: res[f] for f in fields})
    except (ValueError, OSError, AttributeError) as e:  # invalid JSON, schema miss, exhausted retries
        row["error"] = f"{type(e).__name__}: {e}"
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("--out")
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--host", default=os.environ.get("OLLAMA_HOST", "localhost:11434"))
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else HERE / "out" / Path(args.items).name
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        done = {json.loads(line)["id"] for line in out.read_text().splitlines() if line.strip()}
    cb = codebook()
    items = [json.loads(line) for line in Path(args.items).read_text().splitlines() if line.strip()]
    with open(out, "a") as fh:
        for n, item in enumerate(items, 1):
            if item["id"] in done:
                continue
            row = judge_item(item, cb, args.host, args.model)
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            print(f"{n}/{len(items)} {row['id']} {'ERROR' if 'error' in row else 'ok'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
