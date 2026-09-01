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
#
# initdb is also particular about the current effective UID existing in
# /etc/passwd (it looks itself up via getpwuid(), regardless of --username -
# that flag only names the role created *inside* the new cluster). Kubernetes'
# runAsUser doesn't add a matching /etc/passwd entry, so this fails under a
# securityContext-assigned UID unless something fakes that entry first. This
# same image's own /usr/bin/docker-entrypoint.sh hits the identical problem for
# its own (fresh-install) initdb call and works around it with "nss_wrapper"
# (see docker_init_database_dir() in that script, and https://cwrap.org/nss_wrapper.html)
# - replicated here verbatim (translated to POSIX sh; the original is bash) so
# our scratch initdb call gets the same fake passwd/group entry.

data_dir="${PGDATA:-/bitnami/postgresql/data}"

if [ -f "$data_dir/PG_VERSION" ] && { [ ! -f "$data_dir/postgresql.conf" ] || [ ! -f "$data_dir/pg_hba.conf" ]; }; then
  scratch_dir="/tmp/pg-repair-scratch"
  rm -rf "$scratch_dir"

  uid="$(id -u)"
  if ! getent passwd "$uid" >/dev/null 2>&1; then
    for wrapper in /usr/lib/libnss_wrapper.so /lib/libnss_wrapper.so /usr/lib/*/libnss_wrapper.so /lib/*/libnss_wrapper.so; do
      if [ -s "$wrapper" ]; then
        NSS_WRAPPER_PASSWD="$(mktemp)"
        NSS_WRAPPER_GROUP="$(mktemp)"
        export LD_PRELOAD="$wrapper" NSS_WRAPPER_PASSWD NSS_WRAPPER_GROUP
        gid="$(id -g)"
        printf 'postgres:x:%s:%s:PostgreSQL:%s:/bin/false\n' "$uid" "$gid" "$data_dir" > "$NSS_WRAPPER_PASSWD"
        printf 'postgres:x:%s:\n' "$gid" > "$NSS_WRAPPER_GROUP"
        break
      fi
    done
  fi

  if mkdir -p "$scratch_dir" 2>/dev/null; then
    if initdb_output="$(initdb --auth-local=trust --auth-host=trust --username=postgres --no-sync "$scratch_dir" 2>&1)"; then
      initdb_status=0
    else
      initdb_status=$?
    fi
  else
    initdb_output="mkdir $scratch_dir failed"
    initdb_status=1
  fi

  # Cleanup mirrors the real entrypoint's own hygiene: don't leave a stale
  # LD_PRELOAD/NSS_WRAPPER_* pointing at deleted temp files in the environment
  # that execs into the real entrypoint below. Guard on NSS_WRAPPER_PASSWD
  # (only ever set inside the loop above) rather than comparing against
  # $wrapper, which is empty/stale whenever getent already succeeded or no
  # library was found - either way meaning nothing here needs cleaning up.
  if [ -n "${NSS_WRAPPER_PASSWD:-}" ]; then
    rm -f "$NSS_WRAPPER_PASSWD" "$NSS_WRAPPER_GROUP"
    unset LD_PRELOAD NSS_WRAPPER_PASSWD NSS_WRAPPER_GROUP
  fi

  if [ "$initdb_status" -eq 0 ]; then
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
    # Logged, not silently swallowed - this is the only way to debug a failure
    # here, since there's no other output path once the real entrypoint takes over.
    echo "docker-entrypoint-wrapper.sh: scratch initdb repair failed, leaving config as-is:" >&2
    echo "$initdb_output" >&2
  fi

  rm -rf "$scratch_dir"
fi

exec /usr/bin/docker-entrypoint.sh "$@"
