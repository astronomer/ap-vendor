#!/bin/sh
# Create a throwaway realm with a service principal for Postgres and a user
# principal for pgbouncer, export both keytabs to the shared volume, then run the KDC.
set -e

apk add --no-cache -q krb5-server krb5
rm -f /keytabs/*
kdb5_util create -s -r KRB.TEST -P not-a-secret >/dev/null
kadmin.local -q "addprinc -randkey postgres/postgres.krb.test@KRB.TEST" >/dev/null
kadmin.local -q "addprinc -randkey houston@KRB.TEST" >/dev/null
# One-minute tickets, so test.py can check that pgbouncer gets new ones from its
# keytab once they expire. A ticket lasts no longer than the krbtgt principal allows.
for principal in krbtgt/KRB.TEST@KRB.TEST postgres/postgres.krb.test@KRB.TEST houston@KRB.TEST; do
  kadmin.local -q "modprinc -maxlife \"1 minute\" $principal" >/dev/null
done
kadmin.local -q "ktadd -k /keytabs/postgres.keytab postgres/postgres.krb.test@KRB.TEST" >/dev/null
kadmin.local -q "ktadd -k /keytabs/houston.keytab houston@KRB.TEST" >/dev/null
# Postgres and pgbouncer run as non-root users and must be able to read their keytab.
chmod 644 /keytabs/*.keytab
touch /keytabs/ready
echo "KDC ready"
exec krb5kdc -n
