# jhao104/proxy_pool migration

The new deployment lives at `/home/simple/proxy-pool-jhao104` and leaves the
legacy pool at `/home/simple/proxy-pool` untouched. Redis runs in Docker as
`proxy-pool-jhao104-redis`; only the REST API is deployed, on
`127.0.0.1:5011` (there is no separate web UI).

`fetcher/sources/migrated_sources.py` discovers all 84 entries in
`source_manifest.json` and parses text, JSON, HTML table pairs, and
proxy-list.org base64 records. Each source declares `http`, `socks4`,
`socks5`, or `mixed`; the adapters emit a normalized scheme and the validator
uses `requests[socks]` for SOCKS4/5. `migrate_pool.py` imports only legacy
`ok=1` rows, is safe to rerun, and preserves their HTTP transport metadata.

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
treated as HTTP. Query `/get/?protocol=socks4`, `/get/?protocol=socks5`, or
`/get/?protocol=http`; the old `/get/?type=https` filter remains supported.

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

The scheduler is not enabled by the API container. Start it separately only
after reviewing the HTTP-only validator and the 84 adapters:

```bash
docker run -d --name proxy-pool-jhao104-scheduler \
  --network proxy-pool-jhao104-net -e DB_CONN=redis://@proxy-pool-jhao104-redis:6379/0 \
  --entrypoint python proxy-pool-jhao104:local proxyPool.py schedule
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
