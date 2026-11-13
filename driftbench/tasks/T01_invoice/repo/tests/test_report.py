from invoice.report import render_text


def test_header_and_subtotal(sample):
    text = render_text(sample)
    assert "INVOICE 2024-007" in text.splitlines()[0]
    assert text.splitlines()[-1].startswith("Subtotal")
    assert text.splitlines()[-1].endswith("33.50")
