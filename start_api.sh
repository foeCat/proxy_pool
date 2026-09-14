#!/usr/bin/env bash
set -euo pipefail

NETWORK=proxy-pool-jhao104-net
CONTAINER=proxy-pool-jhao104
IMAGE=proxy-pool-jhao104:local
REDIS=proxy-pool-jhao104-redis

if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    docker start "$CONTAINER" >/dev/null 2>&1 || true
else
    docker run -d --restart unless-stopped --name "$CONTAINER" --network "$NETWORK" \
        -p 127.0.0.1:5011:5010 \
        -e HOST=0.0.0.0 -e PORT=5010 \
        -e DB_CONN="redis://@$REDIS:6379/0" "$IMAGE" >/dev/null
fi

for _ in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:5011/count/ >/tmp/proxy-pool-jhao104-count.json; then
        cat /tmp/proxy-pool-jhao104-count.json
        exit 0
    fi
    sleep 1
done

docker logs "$CONTAINER" >&2 || true
exit 1
