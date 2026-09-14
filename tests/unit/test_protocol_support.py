# -*- coding: utf-8 -*-
import json
from unittest.mock import patch

import fakeredis

from db.redisClient import RedisClient
from fetcher.sources.migrated_sources import _decorate, _extract
from helper.proxy import Proxy
from helper.validator import build_proxies


def _client():
    fake = fakeredis.FakeRedis(decode_responses=True, protocol=2)
    with patch("db.redisClient.BlockingConnectionPool"), patch(
        "db.redisClient.Redis", return_value=fake
    ):
        client = RedisClient(host="localhost", port=6379,
                             username=None, password=None, db="0")
    client.changeTable("protocol_test")
    return client, fake


def test_proxy_protocol_and_requests_mapping():
    proxy = Proxy("socks5://user:pass@1.2.3.4:1080")
    assert proxy.protocol == "socks5"
    assert proxy.proxy_url == "socks5://user:pass@1.2.3.4:1080"
    assert build_proxies(proxy)["https"].startswith("socks5h://")


def test_redis_keeps_same_endpoint_for_different_protocols():
    client, _ = _client()
    client.put(Proxy("socks4://1.2.3.4:1080"))
    client.put(Proxy("socks5://1.2.3.4:1080"))
    assert len(client.getAll(protocol="socks4")) == 1
    assert len(client.getAll(protocol="socks5")) == 1
    assert client.getCount()["protocol"] == {"http": 0, "socks4": 1, "socks5": 1}


def test_legacy_json_defaults_to_http():
    client, fake = _client()
    fake.hset(
        "protocol_test", "1.2.3.4:8080", json.dumps({"proxy": "1.2.3.4:8080"})
    )
    assert len(client.getAll(protocol="http")) == 1


def test_migrated_fetcher_preserves_and_adds_schemes():
    values = _extract("socks5://1.2.3.4:1080 5.6.7.8:8080")
    assert "socks5://1.2.3.4:1080" in values
    assert _decorate("5.6.7.8:8080", "socks4") == "socks4://5.6.7.8:8080"


def test_api_protocol_filter(client):
    mocks = client.application._test_mocks
    mocks["get"].return_value = Proxy("socks5://1.2.3.4:1080")
    response = client.get("/get/?protocol=socks5")
    assert response.status_code == 200
    assert response.get_json()["protocol"] == "socks5"
    mocks["get"].assert_called_with(False, protocol="socks5")
