#!/bin/bash
# wait-for-grid.sh

set -e

cmd="$@"

while ! curl -sSL "${SELENIUM_URL}/status" 2>&1 \
        | jq -r '.value.ready' 2>&1 | grep "true" >/dev/null; do
    echo "Waiting for the Grid ${SELENIUM_URL}"
    sleep 1
done

>&2 echo "Selenium Grid is up - executing parser"
exec $cmd