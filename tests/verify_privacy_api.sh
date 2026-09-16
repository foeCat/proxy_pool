#!/usr/bin/env bash
set -euo pipefail

REDIS=proxy-pool-jhao104-redis
KEY=privacy_proxy

cleanup() {
    docker exec "$REDIS" redis-cli DEL "$KEY" >/dev/null
}
trap cleanup EXIT

docker exec "$REDIS" redis-cli HSET "$KEY" socks5 \
    '{"proxy":"1.2.3.4:1080","proxy_url":"socks5://1.2.3.4:1080","protocol":"socks5","priority":50,"exit_ip":"203.0.113.10","privacy_pass":true}' >/dev/null
docker exec "$REDIS" redis-cli HSET "$KEY" socks5h \
    '{"proxy":"2.2.2.2:1080","proxy_url":"socks5h://2.2.2.2:1080","protocol":"socks5h","priority":100,"exit_ip":"203.0.113.11","privacy_pass":true}' >/dev/null
docker exec "$REDIS" redis-cli HSET "$KEY" http \
    '{"proxy":"3.3.3.3:80","protocol":"http","priority":999}' >/dev/null

python3 - <<'PY'
import json
from urllib.request import urlopen

def get(path):
    with urlopen("http://127.0.0.1:5012" + path, timeout=5) as response:
        return json.load(response)

assert get("/get/")["protocol"] == "socks5h"
assert get("/get/?protocol=socks5")["protocol"] == "socks5"
assert get("/get/?protocol=socks5h")["protocol"] == "socks5h"
count = get("/count/")
assert count["count"] == 2
assert count["protocol"]["socks5"] == 1
assert count["protocol"]["socks5h"] == 1
print(json.dumps(count, ensure_ascii=False, sort_keys=True))
PY
