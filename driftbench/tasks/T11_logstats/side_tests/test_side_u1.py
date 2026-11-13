from logstats.privacy import anonymize_ip


def test_u1_anonymize_ipv6():
    assert anonymize_ip("2001:db8:85a3:8d3:1319:8a2e:370:7348") == "2001:db8:85a3::"
    assert anonymize_ip("203.0.113.7") == "203.0.113.0"
