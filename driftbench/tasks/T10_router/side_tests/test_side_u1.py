from microweb.templates import render


def test_u1_upper_and_lower_filters():
    assert render("{{ name|upper }}", {"name": "ada"}) == "ADA"
    assert render("{{ name | lower }}", {"name": "BoB"}) == "bob"
