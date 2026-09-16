#!/usr/bin/env bash
set -euo pipefail

CONTAINER=proxy-pool-jhao104-scheduler
IMAGE=proxy-pool-jhao104:local

if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    docker start "$CONTAINER" >/dev/null 2>&1 || true
else
    docker run -d --restart unless-stopped --name "$CONTAINER" --network host \
        -e DB_CONN=redis://@127.0.0.1:6380/0 \
        --entrypoint python "$IMAGE" proxyPool.py schedule >/dev/null
fi

docker ps --filter "name=^/${CONTAINER}$" --format '{{.Names}} {{.Status}}'
