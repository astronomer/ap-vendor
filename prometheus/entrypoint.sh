#!/bin/sh
set -e

#!/bin/sh
set -e

should_update=false

if [ "$UPDATE_CA_CERTS" = "true" ]; then
    should_update=true
fi

# Check if any custom CA certificates exist
for cert in /usr/local/share/ca-certificates/*.crt; do
    if [ -f "$cert" ]; then
        should_update=true
        break
    fi
done

if [ "$should_update" = "true" ]; then
    echo "Updating CA certificates..."
    update-ca-certificates
fi

exec /bin/prometheus "$@"
