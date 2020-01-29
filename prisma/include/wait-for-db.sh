#!/usr/bin/env sh

set -e

wait_for_it() {
    echo "Waiting for host: $1 $2"
    while ! nc -w 1 -z "$1" "$2"; do
        sleep 1
    done
    echo "Received response from: $1 $2"
}

# parse string like: postgres://postgres:postgres@astronomer-postgresql.astronomer.svc.cluster.local:5432/astronomer_houston
POSTGRES_HOST=$(echo "${PRISMA_DB_URI}" | awk -F@ '{print $2}' | awk -F: '{print $1}')
POSTGRES_PORT=$(echo "${PRISMA_DB_URI}" | awk -F@ '{print $2}' | awk -F: '{print $2}' | awk -F/ '{print $1}')

if [[ -n ${POSTGRES_HOST}  ]]; then
    wait_for_it "$POSTGRES_HOST" "$POSTGRES_PORT"
fi
# Run the original command
exec "$@"
