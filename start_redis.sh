#!/usr/bin/env bash
set -euo pipefail

NETWORK=proxy-pool-jhao104-net
VOLUME=proxy-pool-jhao104-redis-data
CONTAINER=proxy-pool-jhao104-redis

docker network inspect "$NETWORK" >/dev/null 2>&1 || docker network create "$NETWORK" >/dev/null
docker volume inspect "$VOLUME" >/dev/null 2>&1 || docker volume create "$VOLUME" >/dev/null

if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    docker start "$CONTAINER" >/dev/null 2>&1 || true
else
    docker run -d --restart unless-stopped --name "$CONTAINER" --network "$NETWORK" \
        -p 127.0.0.1:6380:6379 -v "$VOLUME":/data \
        redis:7-alpine redis-server --appendonly yes >/dev/null
fi

for _ in $(seq 1 20); do
    if docker exec "$CONTAINER" redis-cli ping 2>/dev/null | grep -q PONG; then
        docker exec "$CONTAINER" redis-cli ping
        exit 0
    fi
    sleep 1
done

echo "Redis did not become ready" >&2
exit 1
