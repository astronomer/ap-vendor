#!/bin/sh
set -e

# PINF-347: on upgrade from a pre-Chainguard image, the real docker-entrypoint.sh
# finds PG_VERSION already present and skips writing postgresql.conf/pg_hba.conf
# (it only does that on first init), so postgres refuses to start. This wrapper
# repairs just that case before handing off to the real entrypoint: run this same
# image's own `initdb` against a throwaway scratch dir (can't target the real,
# already-populated $PGDATA - initdb refuses a non-empty directory) and copy the
# two generated files into place. That way the repair always matches whatever the
# running image's initdb actually produces, instead of a static copy we'd have to maintain.

data_dir="${PGDATA:-/bitnami/postgresql/data}"

if [ -f "$data_dir/PG_VERSION" ] && { [ ! -f "$data_dir/postgresql.conf" ] || [ ! -f "$data_dir/pg_hba.conf" ]; }; then
  scratch_dir="$(mktemp -d /tmp/pg-repair-scratch.XXXXXX 2>/dev/null)" || scratch_dir=""

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

  if [ -n "$scratch_dir" ]; then
    if initdb_output="$(initdb --auth-local=scram-sha-256 --auth-host=scram-sha-256 --username=postgres --no-sync "$scratch_dir" 2>&1)"; then
      initdb_status=0
    else
      initdb_status=$?
    fi
  else
    initdb_output="mkdir $scratch_dir failed"
    initdb_status=1
  fi

  # Only set if the nss_wrapper block above actually ran.
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
      # Remote-connection rule initdb doesn't generate; see comment block above.
      echo "host all all all md5" >> "$data_dir/pg_hba.conf"
    fi
  else
    echo "docker-entrypoint-wrapper.sh: scratch initdb repair failed, leaving config as-is:" >&2
    echo "$initdb_output" >&2
  fi

  rm -rf "$scratch_dir"
fi

exec /usr/bin/docker-entrypoint.sh "$@"
