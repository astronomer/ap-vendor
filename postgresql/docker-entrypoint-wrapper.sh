#!/bin/sh
set -e

# PINF-347: cgr.dev/astronomer.io/ap-postgres's own /usr/bin/docker-entrypoint.sh
# only writes postgresql.conf/pg_hba.conf the first time it initializes a data
# directory, and skips that step whenever it finds an already-initialized one
# (PG_VERSION present) - which is the case on every upgrade from a pre-Chainguard
# image. That leaves upgraded installs with a valid, previously-initialized data
# directory but no server config file at all, and postgres refuses to start:
#
#   postgres: could not access the server configuration file ".../postgresql.conf": No such file or directory
#
# This wrapper repairs ONLY that exact case before handing off to the real
# entrypoint, using the config this same image would have generated on a fresh
# install:
#   - Fresh installs are untouched: PG_VERSION doesn't exist yet, so nothing is
#     copied, and the real entrypoint's normal initdb path runs exactly as before.
#   - Already-healthy installs are untouched: if postgresql.conf/pg_hba.conf
#     already exist, nothing is copied, even if their content has since diverged
#     from this default (e.g. via ALTER SYSTEM, which writes to
#     postgresql.auto.conf and is unaffected either way).
#   - It only ever fires once per data directory: once the file exists, every
#     later start sees the condition as false.

data_dir="${PGDATA:-/bitnami/postgresql/data}"
staging_dir="/opt/astronomer/conf"

if [ -f "$data_dir/PG_VERSION" ] && [ ! -f "$data_dir/postgresql.conf" ] && [ -f "$staging_dir/postgresql.conf" ]; then
  cp "$staging_dir/postgresql.conf" "$data_dir/postgresql.conf"
fi

if [ -f "$data_dir/PG_VERSION" ] && [ ! -f "$data_dir/pg_hba.conf" ] && [ -f "$staging_dir/pg_hba.conf" ]; then
  cp "$staging_dir/pg_hba.conf" "$data_dir/pg_hba.conf"
fi

exec /usr/bin/docker-entrypoint.sh "$@"
