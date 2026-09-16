#!/usr/bin/env python3
"""Rebuild a SOCKS5/SOCKS5H privacy-only Redis pool."""

import hashlib
import hmac
import json
import os
import secrets
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from redis import Redis

import setting

ECHO_URL_TEMPLATE = os.environ.get("ECHO_URL_TEMPLATE", "")
ECHO_SECRET = os.environ.get("ECHO_SECRET", "")
PRIVACY_HASH = os.environ.get("PRIVACY_HASH", "privacy_proxy")
TIMEOUT = float(os.environ.get("PRIVACY_TIMEOUT", "8"))
WORKERS = max(1, int(os.environ.get("PRIVACY_WORKERS", "64")))
LEAK_HEADERS = {"x-forwarded-for", "x-real-ip", "forwarded", "via", "client-ip", "true-client-ip", "x-client-ip", "x-proxyuser-ip", "cf-connecting-ip"}

def redis_client():
    return Redis.from_url(os.environ.get("DB_CONN", setting.DB_CONN), decode_responses=True, socket_timeout=10)

def canonical_signature(nonce, client_ip, headers):
    canonical = json.dumps(headers or {}, sort_keys=True, separators=(",", ":"))
    return hmac.new(ECHO_SECRET.encode(), (nonce + "\n" + client_ip + "\n" + canonical).encode(), hashlib.sha256).hexdigest()

def echo_request(proxy_url=None, dns_mode="remote"):
    nonce = secrets.token_urlsafe(18)
    url = ECHO_URL_TEMPLATE.format(nonce=nonce)
    session = requests.Session()
    session.trust_env = False
    kwargs = {"timeout": TIMEOUT, "headers": {"X-Privacy-Probe": nonce}}
    if proxy_url:
        scheme = "socks5h" if dns_mode == "remote" else "socks5"
        authority = proxy_url.split("://", 1)[-1]
        transport = "%s://%s" % (scheme, authority)
        kwargs["proxies"] = {"http": transport, "https": transport}
    response = session.get(url, **kwargs)
    response.raise_for_status()
    payload = response.json()
    if payload.get("nonce") != nonce:
        raise ValueError("echo nonce mismatch")
    client_ip = str(payload.get("client_ip") or payload.get("ip") or "")
    headers = payload.get("headers") or {}
    if not ECHO_SECRET or not hmac.compare_digest(str(payload.get("signature") or ""), canonical_signature(nonce, client_ip, headers)):
        raise ValueError("echo signature mismatch")
    return client_ip, headers

def proxy_url(record):
    return record.get("proxy_url") or "%s://%s" % (record.get("protocol", "http"), record.get("proxy", ""))

def protocol_variant(record):
    value = str(record.get("proxy_url") or record.get("protocol") or "").lower()
    if value.startswith("socks5h://") or value == "socks5h":
        return "socks5h"
    if value.startswith("socks5://") or value == "socks5":
        return "socks5"
    return ""

def inspect(record, own_ip):
    variant = protocol_variant(record)
    url = proxy_url(record)
    if not variant:
        return record, {"proxy_url": url, "protocol": record.get("protocol", "http"), "privacy_pass": False, "skipped": True, "reason": "only socks5/socks5h allowed"}
    authority = url.split("://", 1)[-1]
    started = time.monotonic()
    row = {"proxy_url": url, "protocol": variant, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    def attempt(mode):
        exit_ip, headers = echo_request(url, dns_mode=mode)
        leaked = [name for name, value in headers.items() if name.lower() in LEAK_HEADERS and own_ip and own_ip in str(value)]
        return exit_ip, leaked

    try:
        exit_ip, leaked = attempt("remote")
        row.update(response_ok=True, exit_ip=exit_ip, header_leak=bool(leaked), leaked_headers=leaked, privacy_pass=bool(exit_ip and exit_ip != own_ip and not leaked), protocol="socks5h", proxy_url="socks5h://%s" % authority, dns_mode="remote", priority=100)
    except Exception as remote_exc:  # noqa: BLE001
        try:
            exit_ip, leaked = attempt("local")
            row.update(response_ok=True, exit_ip=exit_ip, header_leak=bool(leaked), leaked_headers=leaked, privacy_pass=bool(exit_ip and exit_ip != own_ip and not leaked), protocol="socks5", proxy_url="socks5://%s" % authority, dns_mode="local", priority=50)
        except Exception as local_exc:  # noqa: BLE001
            row.update(response_ok=False, privacy_pass=False, error="remote=%s: %s; local=%s: %s" % (type(remote_exc).__name__, remote_exc, type(local_exc).__name__, local_exc))
    row["latency_ms"] = round((time.monotonic() - started) * 1000)
    return record, row

def main():
    if not ECHO_URL_TEMPLATE or not ECHO_SECRET:
        raise SystemExit("ECHO_URL_TEMPLATE and ECHO_SECRET are required")
    client = redis_client()
    records = []
    malformed = 0
    for raw in client.hvals("use_proxy"):
        try:
            records.append(json.loads(raw))
        except (TypeError, ValueError, json.JSONDecodeError):
            malformed += 1
    own_ip, _ = echo_request()
    accepted = {}
    observations = []
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        for record, row in executor.map(lambda item: inspect(item, own_ip), records):
            observations.append(row)
            if row.get("privacy_pass"):
                current = accepted.get(row.get("exit_ip"))
                candidate = {**record, **row}
                if current is None or candidate.get("priority", 0) > current.get("priority", 0):
                    accepted[row["exit_ip"]] = candidate

    report_path = os.environ.get("PRIVACY_REPORT", "privacy-latest.jsonl")
    with open(report_path, "w", encoding="utf-8") as handle:
        for row in observations:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    staging = "%s:next" % PRIVACY_HASH
    client.delete(staging)
    if not accepted:
        print(json.dumps({"checked": len(records), "malformed": malformed,
                          "accepted": 0, "own_ip": own_ip, "pool_updated": False}))
        return
    client.hset(staging, mapping={row["proxy_url"]: json.dumps(row, ensure_ascii=False) for row in accepted.values()})
    client.rename(staging, PRIVACY_HASH)
    print(json.dumps({"checked": len(records), "malformed": malformed,
                      "accepted": len(accepted), "own_ip": own_ip, "pool_updated": True}))

if __name__ == "__main__":
    main()
