# -*- coding: utf-8 -*-
from unittest.mock import patch

from privacy_check import inspect


def test_remote_dns_becomes_high_priority_socks5h():
    record = {"proxy": "1.2.3.4:1080", "protocol": "socks5",
              "proxy_url": "socks5://1.2.3.4:1080"}
    with patch("privacy_check.echo_request", return_value=("203.0.113.10", {})):
        _, row = inspect(record, "198.51.100.7")
    assert row["privacy_pass"] is True
    assert row["protocol"] == "socks5h"
    assert row["proxy_url"] == "socks5h://1.2.3.4:1080"
    assert row["priority"] == 100


def test_local_dns_fallback_stays_lower_priority_socks5():
    record = {"proxy": "1.2.3.4:1080", "protocol": "socks5h",
              "proxy_url": "socks5h://1.2.3.4:1080"}
    with patch("privacy_check.echo_request",
               side_effect=[RuntimeError("remote failed"), ("203.0.113.11", {})]):
        _, row = inspect(record, "198.51.100.7")
    assert row["privacy_pass"] is True
    assert row["protocol"] == "socks5"
    assert row["proxy_url"] == "socks5://1.2.3.4:1080"
    assert row["priority"] == 50


def test_http_and_socks4_are_skipped():
    for protocol in ("http", "socks4"):
        _, row = inspect({"proxy": "1.2.3.4:8080", "protocol": protocol},
                         "198.51.100.7")
        assert row["skipped"] is True
        assert row["privacy_pass"] is False
