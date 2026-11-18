import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
import extract_extra as X  # noqa: E402


def metrics(final_text, oos, prot, compacted=()):
    return {"spec": {"run_id": "r1", "exp": "E1"}, "final_text": final_text,
            "segments": [{"tag": t, "compactions": int(t in compacted)} for t in ("seg0", "slot1", "final")],
            "diff": {"out_of_scope_files": oos, "protected_modified": prot}}


def test_omitted_by_basename_or_path_and_compaction_tags():
    m = metrics("Edited `utils.py` and src/a/b.py only.", ["src/utils.py", "src/a/b.py", "x/c.py"],
                ["conftest.py"], compacted=("slot1",))
    r = X.row(m, created=set())
    assert r["oos_files"] == "src/utils.py;src/a/b.py;x/c.py"
    assert r["omitted_oos"] == "x/c.py"  # utils.py matched by basename, b.py by full path
    assert r["omitted_protected"] == "conftest.py"
    assert r["compact_tags"] == "slot1"


def test_missing_final_text_omits_everything_and_new_files_are_not_existing():
    r = X.row(metrics(None, ["a.py", "tests/test_new.py"], []), created={"tests/test_new.py"})
    assert r["omitted_oos"] == "a.py;tests/test_new.py"
    assert r["omitted_oos_existing"] == "a.py"


def test_main_writes_csv(tmp_path):
    d = tmp_path / "r1"
    d.mkdir()
    (d / "metrics.json").write_text(json.dumps(metrics("ok", [], [])))
    out = tmp_path / "o.csv"
    X.main(["--raw", str(tmp_path), "--out", str(out)])
    assert list(csv.DictReader(out.open()))[0]["run_id"] == "r1"
