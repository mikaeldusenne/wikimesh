#!/usr/bin/env bash
set -Eeuo pipefail

if [[ "$(id -u)" == 0 && -f /data/db/WiredTiger.wt ]]; then
    exec gosu "$(stat -c '%u:%g' /data/db/WiredTiger.wt)" \
        /usr/local/bin/docker-entrypoint.sh "$@"
fi

exec /usr/local/bin/docker-entrypoint.sh "$@"
