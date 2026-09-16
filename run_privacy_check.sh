#!/usr/bin/env bash
set -euo pipefail

: "${ECHO_URL_TEMPLATE:?ECHO_URL_TEMPLATE is required}"
: "${ECHO_SECRET:?ECHO_SECRET is required}"

IMAGE=${PRIVACY_IMAGE:-proxy-pool-jhao104:local}
NETWORK=${PRIVACY_NETWORK:-proxy-pool-jhao104-net}
REDIS=${PRIVACY_REDIS:-proxy-pool-jhao104-redis}
REPORT_DIR=${PRIVACY_REPORT_DIR:-/home/simple/proxy-pool-jhao104/reports/privacy}

mkdir -p "$REPORT_DIR"

docker run --rm --network "$NETWORK" \
    --entrypoint python \
    -e DB_CONN="redis://@$REDIS:6379/0" \
    -e ECHO_URL_TEMPLATE -e ECHO_SECRET \
    -e PRIVACY_HASH=privacy_proxy \
    -e PRIVACY_WORKERS -e PRIVACY_TIMEOUT \
    -e PRIVACY_REPORT=/reports/privacy-latest.jsonl \
    -v "$REPORT_DIR:/reports" \
    "$IMAGE" privacy_check.py
