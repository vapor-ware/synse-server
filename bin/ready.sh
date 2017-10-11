#!/usr/bin/env bash

# ready.sh is the readiness script that can be used (e.g. by kubernetes)
# to determine when the service is ready. it hits the /test endpoint of the
# Flask API. if the response is '{"status": "ok"}', then the server is up
# and ready, otherwise it is not ready yet.

SYNSE_CLIENT_PORT=${SYNSE_CLIENT_PORT:-5000}
SYNSE_VERSION="$(python /synse/synse/version.py api)"

OK=$(curl -s localhost:${SYNSE_CLIENT_PORT}/synse/${SYNSE_CLIENT_PORT}/test | grep "ok")
if [ "$OK" ]; then
    exit 0
else
    exit 1
fi
