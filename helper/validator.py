# -*- coding: utf-8 -*-
"""Proxy format and transport validators.

The public validator hooks still accept the legacy ``host:port`` string.  A
protocol-aware :class:`~helper.proxy.Proxy` may be passed as well, which lets
requests use PySocks for SOCKS4/5 sources.
"""

__author__ = 'JHao'

import re
from urllib.parse import urlsplit

from requests import head
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler
from helper.proxy import Proxy

conf = ConfigHandler()

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func


def _proxy_object(proxy):
    return proxy if isinstance(proxy, Proxy) else Proxy(str(proxy or ""))


def _proxy_value(proxy):
    """Return a normalized proxy URL and protocol for validators."""
    obj = _proxy_object(proxy)
    return obj, obj.proxy_url


def build_proxies(proxy):
    """Build a requests ``proxies`` mapping for HTTP, SOCKS4 or SOCKS5."""
    obj, proxy_url = _proxy_value(proxy)
    if obj.protocol == "http":
        # An HTTP proxy handles both plain HTTP and HTTPS CONNECT requests.
        transport = "http://%s" % obj.proxy
        return {"http": transport, "https": transport}
    if obj.protocol == "socks4":
        transport = "socks4a://%s" % obj.proxy
    elif obj.protocol == "socks5":
        # socks5h delegates DNS resolution to the proxy and works with PySocks.
        transport = "socks5h://%s" % obj.proxy
    else:  # normalize_protocol currently maps unknown values to HTTP.
        transport = proxy_url
    return {"http": transport, "https": transport}


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """Check an IPv4 proxy with optional scheme and credentials."""
    raw = proxy.proxy_url if isinstance(proxy, Proxy) else str(proxy or "").strip()
    if not raw:
        return False
    if "://" in raw:
        parsed = urlsplit(raw)
        if parsed.scheme.lower() not in {"http", "https", "socks4", "socks4a", "socks5", "socks5h"}:
            return False
        if not parsed.hostname or parsed.port is None:
            return False
        raw = parsed.netloc
    return IP_REGEX.fullmatch(raw) is not None


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy):
    """Validate access to the configured HTTP endpoint."""
    try:
        r = head(conf.httpUrl, headers=HEADER, proxies=build_proxies(proxy),
                 timeout=conf.verifyTimeout)
        return r.status_code == 200
    except Exception:
        return False


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy):
    """Validate HTTPS CONNECT access to the configured HTTPS endpoint."""
    try:
        r = head(conf.httpsUrl, headers=HEADER, proxies=build_proxies(proxy),
                 timeout=conf.verifyTimeout, verify=False)
        return r.status_code == 200
    except Exception:
        return False


@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """Extension hook example; always accepts the proxy."""
    return True
