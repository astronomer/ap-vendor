#!/bin/sh

set -e

# In production, we mount the registry TLS certificate
# into /usr/local/share/ca-certificates. This completes
# the certificate installation so we can trust the registry.
if [ "$UPDATE_CA_CERTS" == "true" ]; then
echo "Running update-ca-certificates"
update-ca-certificates
fi

case "$1" in
    *.yaml|*.yml) set -- registry serve "$@" ;;
    serve|garbage-collect|help|-*) set -- registry "$@" ;;
esac

exec "$@"
