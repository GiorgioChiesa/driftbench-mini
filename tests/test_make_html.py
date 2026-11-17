import html
import json
import re

import build_items as bi
import make_html


def test_page_has_codebook_cards_and_no_metadata(raw, tmp_path):
    bi.main(["sample", "--raw", str(raw), "--out", str(tmp_path)])
    items_path = tmp_path / "annot_v1.jsonl"
    out = tmp_path / "annotate_v1.html"
    make_html.main([str(items_path), "--out", str(out)])
    page = out.read_text()
    items = [json.loads(line) for line in items_path.read_text().splitlines()]
    assert page.count("class='card'") == 84
    assert "Choose the ONE label" in page and "localStorage" in page and "Export CSV" in page
    assert f"name='{items[0]['id']}__notes'" in page
    assert all(html.escape(i["card"]) in page for i in items)  # annotator sees the same card as the judge
    manifest = json.loads((tmp_path / "annot_v1_manifest.json").read_text())
    assert not any(m["run_id"] in page for m in manifest.values())
    assert not re.search(r"E1_T01|m-a_|m-b_|_none_r\d|\bgroup\b|manifest", page)
    assert "http://" not in page and "https://" not in page and "src=" not in page
