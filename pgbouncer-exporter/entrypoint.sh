#!/bin/sh
# Backward compatibility shim for prometheus-community/pgbouncer_exporter
# running in a Helm chart designed for jbub/pgbouncer_exporter

# Map DATABASE_URL to PGBOUNCER_EXPORTER_CONNECTION_STRING
export PGBOUNCER_EXPORTER_CONNECTION_STRING="${PGBOUNCER_EXPORTER_CONNECTION_STRING:-$DATABASE_URL}"

# Handle jbub-style subcommands that the prometheus-community binary doesn't support
case "$1" in
  health)
    # jbub's "health" subcommand checks if the exporter is responsive.
    # Replicate by hitting the metrics endpoint.
    wget -qO- --timeout=5 http://localhost:9127/metrics > /dev/null 2>&1
    exit $?
    ;;
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
