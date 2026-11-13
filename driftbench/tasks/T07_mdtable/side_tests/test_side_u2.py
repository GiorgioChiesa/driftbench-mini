from mdtable import render_html


def test_u2_thead_tbody():
    out = render_html(["a", "b"], [[1, 2], [3, 4]])
    assert "<thead>" in out and "</thead>" in out
    assert "<tbody>" in out and "</tbody>" in out
    assert out.index("<th>a</th>") < out.index("</thead>") < out.index("<tbody>") < out.index("<td>1</td>")
