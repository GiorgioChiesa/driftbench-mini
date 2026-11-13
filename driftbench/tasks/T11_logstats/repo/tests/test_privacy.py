from logstats.privacy import anonymize_ip, pseudonymize, scrub


def test_anonymize_ipv4():
    assert anonymize_ip("203.0.113.7") == "203.0.113.0"


def test_pseudonymize_is_stable_and_salted():
    assert pseudonymize("alice", "s1") == pseudonymize("alice", "s1")
    assert pseudonymize("alice", "s1") != pseudonymize("alice", "s2")
    assert len(pseudonymize("alice", "s1")) == 12


def test_scrub(records):
    r = scrub(records[0], "salt")
    assert r.ip == "203.0.113.0"
    assert r.user == pseudonymize("alice", "salt")
    assert scrub(records[2], "salt").user is None
