"""Atomic JSON persistence with a small schema-migration step."""
from __future__ import annotations

import json
import os
from pathlib import Path

SCHEMA_VERSION = 2


def save(records: list[dict], path) -> None:
    """Write ``records`` atomically (temporary file + rename)."""
    path = Path(path)
    payload = {"version": SCHEMA_VERSION, "todos": records}
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load(path) -> list[dict]:
    """Read the todo records stored at ``path``, upgrading old files on the fly."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):  # version 1 files were a bare list of todos
        data = {"version": 1, "todos": data}
    if data.get("version", 1) < SCHEMA_VERSION:
        data = _migrate_v1(data)
    return data["todos"]


def _migrate_v1(data: dict) -> dict:
    """Version 1 only knew id/title/done/tags; priority and created came with version 2."""
    todos = [
        {"id": raw["id"], "title": raw["title"], "done": raw.get("done", False), "tags": raw.get("tags", [])}
        for raw in data["todos"]
    ]
    return {"version": SCHEMA_VERSION, "todos": todos}
