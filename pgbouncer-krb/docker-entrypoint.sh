#!/bin/sh
# Catch SIGTERM (immediate shutdown) and replace it with INT (safe shutdown)
# so pgbouncer can signal postgres clients that it is shutting down.
set -ex

cleanup() {
  echo running cleanup
  kill -INT "$main_proc"
  # The signal interrupted our `wait`, so lets do it again
  wait "$main_proc"
  echo exited with "$?"
}
trap "cleanup" INT TERM

# Run the real command in background so we can still respond to signals.
"$@" &
main_proc=$!
echo "Watching pid $main_proc: $*"
wait
