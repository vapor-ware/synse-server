#!/usr/bin/env bash

# ok.sh
#
# The 'ok' script that can be used to determine when the service is ready
# or healthy. It hits the /test endpoint of the Synse Server API. If the response
# is an OK 200 with 'status' of 'ok', then the server is up and ready and
# considered healthy.
#
# More Info:
#  - https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/
#  - https://docs.docker.com/compose/compose-file/#healthcheck
#  - https://docs.docker.com/engine/reference/builder/#healthcheck

SYNSE_CLIENT_HOST=${SYNSE_CLIENT_HOST:-localhost}
SYNSE_CLIENT_PORT=${SYNSE_CLIENT_PORT:-5000}
TEST_URL="${SYNSE_CLIENT_HOST}:${SYNSE_CLIENT_PORT}/synse/test"

# First, check the HTTP code
CODE=$(curl -s -o /dev/null -w "%{http_code}" ${TEST_URL})
if [ "${CODE}" != "200" ]; then
    echo "Failed check with status code: ${CODE}"
    exit 1
fi

# Then, check the HTTP response JSON
OK=$(curl -s ${TEST_URL} | grep "ok")
if [ ! "$OK" ]; then
    echo "Failed to get {'status': 'ok'} response from Synse Server."
    exit 1
fi

# If we get here, then we passed all checks and are considered
# ready and healthy.
exit 0
