#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Idempotently import available legacy proxies into ProxyPool's Redis hash."""

from __future__ import annotations

import argparse
import json
import sqlite3
from typing import Dict, Tuple
from urllib.parse import urlsplit

import redis

from helper.proxy import Proxy


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-db", required=True, help="legacy pool.db path")
    parser.add_argument("--redis-url", required=True, help="Redis URI")
    parser.add_argument("--table", default="use_proxy", help="Redis hash name")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--normalize-existing", action="store_true",
        help="add explicit protocol metadata to existing Redis JSON values",
    )
    return parser.parse_args()


def _host_port(row: sqlite3.Row) -> str:
    if row["host"] and row["port"]:
        return "%s:%d" % (row["host"], int(row["port"]))
    parsed = urlsplit(row["proxy"])
    if not parsed.hostname or not parsed.port:
        raise ValueError("cannot parse proxy %r" % row["proxy"])
    return "%s:%d" % (parsed.hostname, parsed.port)


def _payload(row: sqlite3.Row) -> Tuple[str, str]:
    raw_proxy = row["proxy"] or _host_port(row)
    protocol = row["scheme"] or None
    proxy_obj = Proxy(raw_proxy, protocol=protocol)
    if proxy_obj.protocol != "socks5":
        raise ValueError("only SOCKS5 can enter the SOCKS5H pool")
    proxy_obj.promote_socks5h()
    proxy = proxy_obj.proxy
    value: Dict[str, object] = {
        "proxy": proxy,
        "protocol": proxy_obj.scheme,
        "proxy_url": proxy_obj.proxy_url,
        "https": False,
        "fail_count": int(row["fail_count"] or 0),
        "region": row["geo"] or "",
        "anonymous": row["anonymity"] or "",
        "source": row["source"] or "legacy-pool",
        "check_count": int(row["success_count"] or 0),
        "last_status": True,
        "last_time": row["last_check"] or row["last_ok"] or "",
    }
    return proxy_obj.storage_key, json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _normalize_existing(client, table: str, batch_size: int) -> int:
    """Annotate legacy values without changing their Redis hash keys."""
    updates: Dict[str, str] = {}
    changed = 0
    for key, raw in client.hscan_iter(table):
        try:
            data = json.loads(raw)
        except (TypeError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        protocol = data.get("protocol") or data.get("scheme")
        if not protocol:
            candidate = data.get("proxy_url") or data.get("proxy") or key
            protocol = Proxy(candidate).protocol if "://" in candidate else "http"
            data["protocol"] = protocol
            updates[key] = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            changed += 1
        if len(updates) >= batch_size:
            client.hset(table, mapping=updates)
            updates.clear()
    if updates:
        client.hset(table, mapping=updates)
    return changed


def main() -> int:
    args = _args()
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be positive")
    source = sqlite3.connect(
        "file:%s?mode=ro" % args.source_db, uri=True, check_same_thread=False
    )
    source.row_factory = sqlite3.Row
    rows = source.execute(
        "SELECT proxy, scheme, host, port, fail_count, geo, anonymity, source, "
        "success_count, last_check, last_ok FROM proxies "
        "WHERE ok=1 AND (lower(scheme) IN ('socks5', 'socks5h') "
        "OR lower(proxy) LIKE 'socks5://%' OR lower(proxy) LIKE 'socks5h://%') "
        "ORDER BY proxy"
    )
    client = None if args.dry_run else redis.Redis.from_url(
        args.redis_url, decode_responses=True
    )
    normalized = 0
    if client is not None and args.normalize_existing:
        normalized = _normalize_existing(client, args.table, args.batch_size)
    imported = updated = skipped = 0
    batch: Dict[str, str] = {}
    for row in rows:
        try:
            proxy, value = _payload(row)
        except (TypeError, ValueError) as exc:
            skipped += 1
            print("skip %s: %s" % (row["proxy"], exc))
            continue
        if client is not None and client.hexists(args.table, proxy):
            updated += 1
        else:
            imported += 1
        batch[proxy] = value
        if len(batch) >= args.batch_size:
            if client is not None:
                client.hset(args.table, mapping=batch)
            batch.clear()
    if batch and client is not None:
        client.hset(args.table, mapping=batch)
    source.close()
    print(json.dumps({
        "source_ok": imported + updated + skipped,
        "inserted": imported,
        "updated": updated,
        "skipped": skipped,
        "normalized_existing": normalized,
        "dry_run": args.dry_run,
        "table": args.table,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
