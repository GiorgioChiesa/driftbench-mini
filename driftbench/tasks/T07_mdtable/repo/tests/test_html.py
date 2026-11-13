from mdtable import render_html


def test_render_html(fruit):
    headers, rows = fruit
    out = render_html(headers, rows).splitlines()
    assert out[0] == "<table>"
    assert out[1] == "  <tr><th>Fruit</th><th>Qty</th></tr>"
    assert out[4] == "  <tr><td>kiwi</td><td></td></tr>"
    assert out[-1] == "</table>"


def test_cells_are_escaped():
    out = render_html(["a"], [["<b>&"]])
    assert "<td>&lt;b&gt;&amp;</td>" in out


def test_caption():
    assert "  <caption>Stock</caption>" in render_html(["a"], [], caption="Stock")
