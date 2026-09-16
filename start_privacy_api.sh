#!/usr/bin/env bash
set -euo pipefail

# Separate API process for privacy_proxy. The existing 5011/use_proxy
# container is intentionally left untouched.
NETWORK=proxy-pool-jhao104-net
CONTAINER=proxy-pool-jhao104-privacy
IMAGE=proxy-pool-jhao104:local
REDIS=proxy-pool-jhao104-redis

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    docker build -t "$IMAGE" .
fi

if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    docker start "$CONTAINER" >/dev/null 2>&1 || true
else
    docker run -d --restart unless-stopped --name "$CONTAINER" --network "$NETWORK" \
        -p 127.0.0.1:5012:5010 \
        -e HOST=0.0.0.0 -e PORT=5010 -e TABLE_NAME=privacy_proxy \
        -e DB_CONN="redis://@$REDIS:6379/0" "$IMAGE" >/dev/null
fi

for _ in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:5012/count/; then
        exit 0
    fi
    sleep 1
done

docker logs "$CONTAINER" >&2 || true
exit 1
