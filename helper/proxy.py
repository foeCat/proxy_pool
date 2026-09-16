# -*- coding: utf-8 -*-
"""Protocol-aware proxy value object."""

__author__ = 'JHao'

import json
from urllib.parse import quote, urlsplit


PROTOCOL_ALIASES = {
    "http": "http",
    "https": "http",      # HTTPS proxy lists still use HTTP CONNECT.
    "socks": "socks5",
    "socks4": "socks4",
    "socks4a": "socks4",
    "socks5": "socks5",
    "socks5h": "socks5",
}


def normalize_protocol(protocol):
    return PROTOCOL_ALIASES.get(str(protocol or "http").lower(), "http")


def _split_proxy(value, protocol=None):
    raw = str(value or "").strip()
    if "://" not in raw:
        return normalize_protocol(protocol), raw
    parsed = urlsplit(raw)
    selected = normalize_protocol(parsed.scheme)
    host = parsed.hostname or ""
    if ":" in host and not host.startswith("["):
        host = "[%s]" % host
    try:
        port = parsed.port
    except ValueError:
        port = None
    hostport = host if port is None else "%s:%d" % (host, port)
    if parsed.username is not None:
        user = quote(parsed.username, safe="")
        password = quote(parsed.password or "", safe="")
        hostport = "%s:%s@%s" % (user, password, hostport)
    return selected, hostport


class Proxy(object):

    def __init__(self, proxy, fail_count=0, region="", anonymous="",
                 source="", check_count=0, last_status="", last_time="",
                 https=False, protocol=None, **metadata):
        raw_proxy = str(proxy or "")
        if "://" in raw_proxy:
            raw_scheme = raw_proxy.split("://", 1)[0].lower()
        else:
            raw_scheme = str(protocol or "").lower()
        self._scheme = raw_scheme if raw_scheme in {"socks5", "socks5h"} else ""
        self._protocol, self._proxy = _split_proxy(proxy, protocol)
        self._fail_count = fail_count
        self._region = region
        self._anonymous = anonymous
        self._source = source.split('/')
        self._check_count = check_count
        self._last_status = last_status
        self._last_time = last_time
        self._https = https
        self._metadata = metadata

    @classmethod
    def createFromJson(cls, proxy_json):
        data = json.loads(proxy_json)
        extras = {key: data[key] for key in ("privacy_pass", "exit_ip", "header_leak", "latency_ms", "dns_mode", "priority", "checked_at") if key in data}
        return cls(proxy=data.get("proxy_url") or data.get("proxy", ""),
                   protocol=data.get("protocol") or data.get("scheme"),
                   fail_count=data.get("fail_count", 0),
                   region=data.get("region", ""),
                   anonymous=data.get("anonymous", ""),
                   source=data.get("source", ""),
                   check_count=data.get("check_count", 0),
                   last_status=data.get("last_status", ""),
                   last_time=data.get("last_time", ""),
                   https=data.get("https", False), **extras)

    @property
    def proxy(self):
        return self._proxy

    @property
    def protocol(self):
        return self._protocol

    @property
    def scheme(self):
        return self.protocol

    @property
    def proxy_url(self):
        return "%s://%s" % (self._scheme or self.protocol, self.proxy)

    @property
    def storage_key(self):
        # Keep legacy HTTP keys readable while separating SOCKS transports.
        return self.proxy if self.protocol == "http" else self.proxy_url

    @property
    def fail_count(self):
        return self._fail_count

    @property
    def region(self):
        return self._region

    @property
    def anonymous(self):
        return self._anonymous

    @property
    def source(self):
        return '/'.join(self._source)

    @property
    def check_count(self):
        return self._check_count

    @property
    def last_status(self):
        return self._last_status

    @property
    def last_time(self):
        return self._last_time

    @property
    def https(self):
        return self._https

    @property
    def to_dict(self):
        data = {"proxy": self.proxy,
                "https": self.https,
                "fail_count": self.fail_count,
                "region": self.region,
                "anonymous": self.anonymous,
                "source": self.source,
                "check_count": self.check_count,
                "last_status": self.last_status,
                "last_time": self.last_time}
        if self.protocol != "http":
            data.update({"protocol": self._scheme or self.protocol, "proxy_url": self.proxy_url})
        if self._metadata:
            data.update(self._metadata)
        return data

    @property
    def to_json(self):
        return json.dumps(self.to_dict, ensure_ascii=False)

    @fail_count.setter
    def fail_count(self, value):
        self._fail_count = value

    @check_count.setter
    def check_count(self, value):
        self._check_count = value

    @last_status.setter
    def last_status(self, value):
        self._last_status = value

    @last_time.setter
    def last_time(self, value):
        self._last_time = value

    @https.setter
    def https(self, value):
        self._https = value

    @region.setter
    def region(self, value):
        self._region = value

    def add_source(self, source_str):
        if source_str:
            self._source.append(source_str)
            self._source = list(set(self._source))
