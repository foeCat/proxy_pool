# jhao104/proxy_pool migration

The new deployment lives at `/home/simple/proxy-pool-jhao104` and leaves the
legacy pool at `/home/simple/proxy-pool` untouched. Redis runs in Docker as
`proxy-pool-jhao104-redis`; the single `use_proxy` hash is the production pool
and the REST API listens on `127.0.0.1:5011` (there is no web UI or second
privacy pool).

`fetcher/sources/migrated_sources.py` discovers all 84 entries in
`source_manifest.json` and parses text, JSON, HTML table pairs, and
proxy-list.org base64 records. Each source declares `http`, `socks4`,
`socks5`, or `mixed`; collection discards bare, HTTP and SOCKS4 candidates.
SOCKS5 candidates are validated through `socks5h://`, then stored as SOCKS5H.
`migrate_pool.py` imports only legacy `ok=1` SOCKS5 rows and promotes them to
SOCKS5H. It is safe to rerun.

The one-off migration command (safe to rerun) is:

```bash
docker run --rm --network proxy-pool-jhao104-net \
  -v /home/simple/proxy-pool:/source:ro --entrypoint python \
  proxy-pool-jhao104:local migrate_pool.py \
  --source-db /source/pool.db \
  --redis-url redis://@proxy-pool-jhao104-redis:6379/0
```

Add `--normalize-existing` when upgrading pre-existing Redis values to include
an explicit `protocol` field. Legacy values without that field are always
treated as HTTP. Normally call `/get/`; `/get/?protocol=socks5h` provides the
same pool with an explicit protocol filter.

## Operate

```bash
docker start proxy-pool-jhao104-redis proxy-pool-jhao104
curl -s http://127.0.0.1:5011/get/
docker run --rm --network proxy-pool-jhao104-net \
  --entrypoint python proxy-pool-jhao104:local proxyPool.py fetcher
```

There is no separate web UI. The container exposes the REST API only; the
container's internal port is `5010`, published locally as `127.0.0.1:5011` to
avoid the legacy API on port `5010`.

The scheduler is not enabled by the API container. It uses the 84 registered
adapters as candidate sources but retains only SOCKS5 endpoints that pass a
SOCKS5H (proxy-side DNS) request:

```bash
./start_scheduler.sh
```

## Rollback

```bash
docker stop proxy-pool-jhao104 2>/dev/null || true
docker rm proxy-pool-jhao104 2>/dev/null || true
docker stop proxy-pool-jhao104-redis 2>/dev/null || true
```

The old API/timers can be restored independently with `systemctl start
pool-check.timer pool-fetch.timer`; port 5010 and the original SQLite database
remain unchanged. A pre-migration copy is beside it as
`pool.db.backup-20260914-before-jhao104`.
