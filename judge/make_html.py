"""Build the self-contained annotation page from an items JSONL (spec: judge/DESIGN.md).

  python3 judge/make_html.py judge/items/annot_v1.jsonl [--out judge/items/annotate_v1.html]

The page holds the codebook and, per item, only the opaque id and the rendered text: no manifest data.
Answers autosave to localStorage; "Export CSV" downloads id,label,recall,claims_complete,
main_accomplishment,notes.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

import judge

HERE = Path(__file__).resolve().parent
COLUMNS = ["id", "label", "recall", "claims_complete", "main_accomplishment", "notes"]

CSS = """body{font:15px/1.4 sans-serif;max-width:60em;margin:1em auto;padding:0 1em}
pre{white-space:pre-wrap;background:#f6f6f6;padding:.6em;border-radius:4px}
.card{border:1px solid #bbb;border-radius:6px;padding:.8em;margin:1.5em 0}
.card h3{margin:.2em 0}.card h4{margin:.8em 0 .2em}label{margin-right:1em;white-space:nowrap}
textarea{width:100%}#bar{position:sticky;top:0;background:#fff;padding:.4em 0;border-bottom:1px solid #ccc}"""

JS = """
const KEY = 'annotate_v1';
let saved = {};
try { saved = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
const inputs = [...document.querySelectorAll('input[type=radio], textarea')];
function value(el) { return el.type === 'radio' ? (el.checked ? el.value : null) : el.value; }
function collect() {
  const out = {};
  for (const el of inputs) { const v = value(el); if (v) out[el.name] = v; }
  return out;
}
for (const el of inputs) {
  if (el.type === 'radio') el.checked = saved[el.name] === el.value; else el.value = saved[el.name] || '';
  el.addEventListener('change', save); el.addEventListener('input', save);
}
function save() {
  try { localStorage.setItem(KEY, JSON.stringify(collect())); } catch (e) {}
  const a = collect();  // an item counts once every one of its fields is answered
  document.getElementById('count').textContent = IDS.filter(id => NEED[id].every(f => a[id + '__' + f])).length;
}
function q(s) { return '"' + String(s || '').replace(/"/g, '""') + '"'; }
function exportCsv() {
  const a = collect(), rows = [COLUMNS.join(',')];
  for (const id of IDS) rows.push(COLUMNS.map(c => c === 'id' ? id : q(a[id + '__' + c])).join(','));
  const url = URL.createObjectURL(new Blob([rows.join('\\n') + '\\n'], {type: 'text/csv'}));
  const l = document.createElement('a'); l.href = url; l.download = 'annotations_v1.csv'; l.click();
}
save();
"""


def card(item: dict, fields: dict) -> str:
    i = html.escape(item["id"])
    parts = [f"<div class='card'><h3>Item {i}</h3>"]
    for head, text in judge.sections(item):
        parts.append(f"<h4>{html.escape(head)}</h4><pre>{html.escape(text)}</pre>")
    for field, labels in fields.items():
        radios = "".join(f"<label><input type='radio' name='{i}__{field}' value='{lab}'> {lab}</label>"
                         for lab in labels)
        parts.append(f"<p><b>{field}</b>: {radios}</p>")
    parts.append(f"<textarea name='{i}__notes' rows='2' placeholder='notes'></textarea></div>")
    return "".join(parts)


def build_page(items: list, codebook_text: str) -> str:
    fields = {t: f for t, (_, f) in judge.codebook().items()}
    cards = "".join(card(it, fields[it["type"]]) for it in items)
    ids = json.dumps([it["id"] for it in items])
    need = json.dumps({it["id"]: list(fields[it["type"]]) for it in items})
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>Annotation v1</title>"
            f"<style>{CSS}</style></head><body>"
            f"<div id='bar'>Annotated: <span id='count'>0</span> / {len(items)} "
            f"<button onclick='exportCsv()'>Export CSV</button> (answers autosave in this browser)</div>"
            f"<h2>Codebook</h2><pre>{html.escape(codebook_text)}</pre>{cards}"
            f"<script>const IDS = {ids}; const NEED = {need}; const COLUMNS = {json.dumps(COLUMNS)};{JS}</script></body></html>")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("--out", default=str(HERE / "items" / "annotate_v1.html"))
    args = ap.parse_args(argv)
    items = [json.loads(line) for line in Path(args.items).read_text().splitlines() if line.strip()]
    Path(args.out).write_text(build_page(items, (HERE / "CODEBOOK.md").read_text()))
    print(f"{len(items)} items -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
