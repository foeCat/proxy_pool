# -*- coding: utf-8 -*-
"""Adapters for the 84 entries in source_manifest.json.

The upstream project expects fetchers to yield ``host:port`` strings.  One
dynamic BaseFetcher subclass is exposed for each manifest entry.
"""

from __future__ import annotations

import base64
import html
import ipaddress
import json
import os
import re
from typing import Any, Iterable, Iterator, List, Optional

from fetcher.baseFetcher import BaseFetcher
from helper.proxy import Proxy
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

_LOGGER = LogHandler("migrated_fetchers")
_IP = r"(?:\d{1,3}\.){3}\d{1,3}"
_PAIR_RE = re.compile(r"(?<![\d.])(" + _IP + r")\s*:\s*(\d{1,5})(?!\d)")
_SCHEME_PAIR_RE = re.compile(
    r"(?P<scheme>https?|socks4a?|socks5h?)://"
    r"(?P<authority>(?:[^\s/@:]+:[^\s/@:]+@)?" + _IP + r":\d{1,5})", re.I
)
_HTML_PAIR_RE = re.compile(
    r"<td[^>]*>\s*(" + _IP + r")\s*</td>\s*"
    r"<td[^>]*>\s*(\d{1,5})\s*</td>", re.I | re.S
)
_B64_PROXY_RE = re.compile(r"Proxy\(\s*['\"]([A-Za-z0-9+/=]+)['\"]\s*\)")


def _valid_pair(host: str, port: str) -> Optional[str]:
    try:
        ipaddress.ip_address(host)
        value = int(port)
    except (ValueError, TypeError):
        return None
    if not 1 <= value <= 65535:
        return None
    return "%s:%d" % (host, value)


def _pairs_from_text(text: str) -> Iterator[str]:
    for scheme, authority in _SCHEME_PAIR_RE.findall(text or ""):
        host, port = authority.rsplit(":", 1)
        value = _valid_pair(host.rsplit("@", 1)[-1], port)
        if value:
            prefix = authority[:-len(value)] if authority.endswith(value) else ""
            if prefix:
                value = prefix + value
            yield "%s://%s" % (scheme.lower(), value)
    for host, port in _PAIR_RE.findall(text or ""):
        value = _valid_pair(host, port)
        if value:
            yield value
    for host, port in _HTML_PAIR_RE.findall(html.unescape(text or "")):
        value = _valid_pair(host, port)
        if value:
            yield value
    for encoded in _B64_PROXY_RE.findall(text or ""):
        try:
            decoded = base64.b64decode(encoded + "=" * (-len(encoded) % 4))
            decoded_text = decoded.decode("ascii", "ignore")
        except (ValueError, UnicodeError):
            continue
        for host, port in _PAIR_RE.findall(decoded_text):
            value = _valid_pair(host, port)
            if value:
                yield value


def _json_values(node: Any) -> Iterable[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        host = node.get("ip") or node.get("host") or node.get("address")
        port = node.get("port")
        if host and port:
            protocol = node.get("protocol") or node.get("scheme")
            value = "%s:%s" % (host, port)
            yield "%s://%s" % (protocol, value) if protocol else value
        proxy = node.get("proxy") or node.get("proxy_url")
        if isinstance(proxy, str):
            yield proxy
        for value in node.values():
            yield from _json_values(value)
    elif isinstance(node, list):
        for value in node:
            yield from _json_values(value)


def _extract(body: str) -> List[str]:
    candidates: List[str] = list(_pairs_from_text(body))
    try:
        parsed = json.loads(body)
    except (TypeError, ValueError):
        parsed = None
    if parsed is not None:
        for value in _json_values(parsed):
            candidates.extend(_pairs_from_text(value))
    return list(dict.fromkeys(candidates))


def _decorate(proxy: str, source_protocol: str) -> str:
    """Attach a transport scheme, normalizing HTTPS proxy lists to HTTP."""
    obj = Proxy(proxy, protocol=None if source_protocol == "mixed" else source_protocol)
    return obj.proxy_url


def _fetch(self: BaseFetcher) -> Iterator[str]:
    try:
        response = WebRequest().get(
            self.url, timeout=12, retry_time=1, verify=False,
            header={"Accept": "*/*"},
        )
        values = (_decorate(proxy, self.source_protocol)
                  for proxy in _extract(response.text))
        for proxy in self.yieldUniqueProxies(values):
            yield proxy
    except Exception as exc:
        _LOGGER.warning("ProxyFetch - %s: %s", self.name, exc)


def _manifest_path() -> str:
    configured = os.environ.get("PROXY_POOL_SOURCE_MANIFEST")
    if configured:
        return configured
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "source_manifest.json"),
        os.path.join(here, "..", "..", "source_manifest.json"),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return candidates[-1]


def _class_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", name).title().replace(" ", "")
    return "Migrated%sFetcher" % (cleaned or "Source")


def _make_fetcher(entry: dict, class_name: str):
    attrs = {
        "__module__": __name__,
        "name": entry["name"],
        "url": entry["url"],
        "source_protocol": entry.get("proto", "mixed"),
        "source_region": entry.get("region", ""),
        "enabled": True,
        "fetch": _fetch,
    }
    return type(class_name, (BaseFetcher,), attrs)


with open(_manifest_path(), "r", encoding="utf-8") as _handle:
    _manifest = json.load(_handle)
for _index, _entry in enumerate(_manifest, 1):
    _base_name = _class_name(_entry["name"])
    _generated_name = _base_name
    if _generated_name in globals():
        _generated_name = "%s%02d" % (_base_name, _index)
    globals()[_generated_name] = _make_fetcher(_entry, _generated_name)
