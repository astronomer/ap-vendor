#!/bin/sh
set -ex

cleanup() {
  echo running cleanup
  kill -INT "$main_proc"
  # The signal interrupted our `wait`, so lets do it again
  wait "$main_proc"
  echo exited with "$?"
}
# SIGTERM - Immediate shutdown for pgbouncer process,
# but we would like to catch such signal and replace with SIGINT (Safe shutdown.)
trap "cleanup" TERM

exec "$@" &
main_proc=$!
echo "Waiting for it to complete"
wait
