#!/bin/sh

set -e

# In production, we mount the registry TLS certificate
# into /usr/local/share/ca-certificates. This completes
# the certificate installation so we can trust the registry.
if [ "$UPDATE_CA_CERTS" = "true" ]; then
  echo "Running update-ca-certificates"
  update-ca-certificates
fi

# this if will check if the first argument is a flag
# but only works if all arguments require a hyphenated flag
# -v; -SL; -f arg; etc will work, but not arg1 arg2
if [ "$#" -eq 0 ] || [ "${1#-}" != "$1" ]; then
    set -- alertmanager "$@"
fi

# else default to run whatever the user wanted like "bash" or "sh"
exec "$@"
