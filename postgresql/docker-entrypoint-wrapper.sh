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
# entrypoint, using this same image's own real `initdb` to generate the missing
# file(s) - not a static copy we maintain ourselves:
#   - Fresh installs are untouched: PG_VERSION doesn't exist yet, so the repair
#     condition is false, and the real entrypoint's normal initdb path runs
#     exactly as before.
#   - Already-healthy installs are untouched: if postgresql.conf/pg_hba.conf
#     already exist, nothing is regenerated, even if their content has since
#     diverged from a fresh default (e.g. via ALTER SYSTEM, which writes to
#     postgresql.auto.conf and is unaffected either way).
#   - It only ever fires once per data directory: once the file exists, every
#     later start sees the condition as false.
#
# Why a scratch initdb instead of shipping static postgresql.conf/pg_hba.conf
# copies (the previous version of this fix, see git history):
#   `initdb` refuses to initialize a non-empty data directory, so it can't be
#   run against the real, already-populated $PGDATA - but it can be run
#   against an empty scratch directory, and the two files it generates there
#   are exactly what a fresh install would have produced. That means this
#   always reflects whatever the *currently running* image's initdb actually
#   does - including any future Chainguard/upstream changes to the sample
#   templates or default auth logic - instead of a byte-for-byte snapshot we
#   captured once and would silently go stale as the base image evolves.
#   (`postgresql.conf` and `pg_hba.conf` are kept, commented out of use, in
#   this directory for reference/rollback - see the Dockerfile.)
#
# The one thing initdb's own output does NOT cover: this chart's Service
# accepts connections from other pods (Houston, in particular), which aren't
# loopback traffic and so need a remote auth rule that initdb's sample-derived
# pg_hba.conf never includes on its own. That one line is still hand-maintained
# below. `md5` (not `scram-sha-256`) is used deliberately: it authenticates
# SCRAM-hashed passwords exactly the same way, but also covers any role whose
# password predates Postgres's SCRAM default and was never rotated - see
# PINF-347 review discussion.

data_dir="${PGDATA:-/bitnami/postgresql/data}"

if [ -f "$data_dir/PG_VERSION" ] && { [ ! -f "$data_dir/postgresql.conf" ] || [ ! -f "$data_dir/pg_hba.conf" ]; }; then
  scratch_dir="/tmp/pg-repair-$$"

  if mkdir -p "$scratch_dir" 2>/dev/null \
    && initdb --auth-local=trust --auth-host=trust --username=postgres --no-sync "$scratch_dir" >/dev/null 2>&1; then

    if [ ! -f "$data_dir/postgresql.conf" ] && [ -f "$scratch_dir/postgresql.conf" ]; then
      cp "$scratch_dir/postgresql.conf" "$data_dir/postgresql.conf"
    fi

    if [ ! -f "$data_dir/pg_hba.conf" ] && [ -f "$scratch_dir/pg_hba.conf" ]; then
      cp "$scratch_dir/pg_hba.conf" "$data_dir/pg_hba.conf"
      # Remote (non-loopback) connections, e.g. from Houston in another pod -
      # not something initdb generates on its own. See comment block above.
      echo "host all all all md5" >> "$data_dir/pg_hba.conf"
    fi
  else
    echo "docker-entrypoint-wrapper.sh: scratch initdb repair failed; leaving config as-is" >&2
  fi

  rm -rf "$scratch_dir"
fi

exec /usr/bin/docker-entrypoint.sh "$@"
