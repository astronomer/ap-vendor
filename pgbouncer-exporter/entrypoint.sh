#!/bin/sh
# Backward compatibility shim for prometheus-community/pgbouncer_exporter
# running in a Helm chart designed for jbub/pgbouncer_exporter
#
# Handles two compatibility gaps:
# 1. ENV: Helm chart injects DATABASE_URL, prometheus-community expects PGBOUNCER_EXPORTER_CONNECTION_STRING
# 2. Subcommands: jbub uses "server" subcommand to start, prometheus-community takes no subcommand

# Map DATABASE_URL to PGBOUNCER_EXPORTER_CONNECTION_STRING (if not already set)
export PGBOUNCER_EXPORTER_CONNECTION_STRING="${PGBOUNCER_EXPORTER_CONNECTION_STRING:-$DATABASE_URL}"

case "$1" in
  server)
    # jbub's "server" subcommand starts the exporter.
    # prometheus-community binary starts directly with no subcommand.
    shift
    exec pgbouncer_exporter "$@"
    ;;
  *)
    exec pgbouncer_exporter "$@"
    ;;
esac
