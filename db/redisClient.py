# -*- coding: utf-8 -*-
"""Redis storage adapter with protocol-aware proxy keys and filters."""

__author__ = 'JHao'

import json
from random import choice

from redis import Redis
from redis.connection import BlockingConnectionPool
from redis.exceptions import ConnectionError, ResponseError, TimeoutError

from handler.logHandler import LogHandler
from helper.proxy import Proxy, normalize_protocol


class RedisClient(object):
    """Store proxy JSON values in a Redis hash.

    HTTP records retain the upstream ``host:port`` key. SOCKS records use a
    scheme-prefixed key so ``1.2.3.4:1080`` can exist as both SOCKS4 and SOCKS5.
    """

    def __init__(self, **kwargs):
        self.name = ""
        kwargs.pop("username")
        self.__conn = Redis(connection_pool=BlockingConnectionPool(
            decode_responses=True, timeout=5, socket_timeout=5, protocol=2,
            **kwargs))

    @staticmethod
    def _data(value):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}

    @classmethod
    def _protocol(cls, value):
        data = cls._data(value)
        return normalize_protocol(data.get("protocol") or data.get("scheme"))

    @classmethod
    def _protocol_variant(cls, value):
        """Return the exact SOCKS5 transport variant when available."""
        data = cls._data(value)
        proxy_url = str(data.get("proxy_url") or "").lower()
        raw = proxy_url.split("://", 1)[0] if "://" in proxy_url else ""
        if not raw:
            raw = str(data.get("protocol") or data.get("scheme") or "").lower()
        return raw if raw in {"socks5", "socks5h"} else cls._protocol(value)

    @classmethod
    def _key_for_value(cls, value):
        data = cls._data(value)
        try:
            return Proxy.createFromJson(value).storage_key
        except (TypeError, ValueError, KeyError):
            return data.get("proxy_url") or data.get("proxy", "")

    @classmethod
    def _matches(cls, value, https=False, protocol=None):
        data = cls._data(value)
        if https and not data.get("https"):
            return False
        if protocol is None:
            return True
        requested = str(protocol).lower()
        if requested in {"socks5", "socks5h"}:
            return cls._protocol_variant(value) == requested
        return cls._protocol(value) == normalize_protocol(requested)

    def _values(self):
        return list(self.__conn.hvals(self.name))

    def get(self, https=False, protocol=None):
        values = [value for value in self._values()
                  if self._matches(value, https=https, protocol=protocol)]
        return choice(values) if values else None

    def put(self, proxy_obj):
        return self.__conn.hset(self.name, proxy_obj.storage_key, proxy_obj.to_json)

    def pop(self, https=False, protocol=None):
        value = self.get(https, protocol=protocol)
        if value:
            self.__conn.hdel(self.name, self._key_for_value(value))
        return value if value else None

    def delete(self, proxy_str, protocol=None):
        value = str(proxy_str or "").strip()
        if "://" not in value:
            value = Proxy(value, protocol=protocol).storage_key
        return self.__conn.hdel(self.name, value)

    def exists(self, proxy_str, protocol=None):
        value = str(proxy_str or "").strip()
        if "://" not in value:
            value = Proxy(value, protocol=protocol).storage_key
        return self.__conn.hexists(self.name, value)

    def update(self, proxy_obj):
        return self.__conn.hset(self.name, proxy_obj.storage_key, proxy_obj.to_json)

    def getAll(self, https=False, protocol=None):
        return [value for value in self._values()
                if self._matches(value, https=https, protocol=protocol)]

    def clear(self):
        return self.__conn.delete(self.name)

    def getCount(self):
        values = self._values()
        protocol_count = {"http": 0, "socks4": 0, "socks5": 0}
        https_count = 0
        for value in values:
            variant = self._protocol_variant(value)
            if variant not in protocol_count:
                protocol_count[variant] = 0
            protocol_count[variant] += 1
            if self._data(value).get("https"):
                https_count += 1
        return {"total": len(values), "https": https_count, "protocol": protocol_count}

    def changeTable(self, name):
        self.name = name

    def test(self):
        log = LogHandler('redis_client')
        try:
            self.getCount()
        except TimeoutError as e:
            log.error('redis connection time out: %s' % str(e), exc_info=True)
            return e
        except ConnectionError as e:
            log.error('redis connection error: %s' % str(e), exc_info=True)
            return e
        except ResponseError as e:
            log.error('redis connection error: %s' % str(e), exc_info=True)
            return e
