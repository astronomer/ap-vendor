## Pgbouncer with custom gss support

### Environment variables

```
# Manage to generate example of /etc/krb5
GENERATE_KRB5_CONFIG=true
```

Without specifying it:

```bash
docker run --env GENERATE_KRB5_CONFIG t
skipping generating /etc/krb5.conf
+ '[[' -z  ]]
+ echo 'skipping generating /etc/krb5.conf'
+ PG_CONFIG_DIR=/etc/pgbouncer
+ '[' -n  ]
+ _AUTH_FILE=/etc/pgbouncer/userlist.txt
+ '[' '!' -e /etc/pgbouncer/userlist.txt ]
+ '[' -n  -a -n  -a -e /etc/pgbouncer/userlist.txt ]
+ '[' '!' -f /etc/pgbouncer/pgbouncer.ini ]
+ exec pgbouncer -u pgbouncer /etc/pgbouncer/pgbouncer.ini
2022-07-28 14:59:38.484 UTC [1] LOG kernel file descriptor limit: 1048576 (hard: 1048576); max_client_conn: 100, max expected fd use: 112
2022-07-28 14:59:38.484 UTC [1] LOG listening on 0.0.0.0:6432
2022-07-28 14:59:38.484 UTC [1] LOG listening on unix:/tmp/.s.PGSQL.6432
2022-07-28 14:59:38.484 UTC [1] LOG process up: PgBouncer 1.17.0, libevent 2.1.12-stable (epoll), adns: c-ares 1.18.1, tls: OpenSSL 1.1.1q  5 Jul 2022
^C2022-07-28 14:59:43.161 UTC [1] LOG got SIGINT, shutting down
2022-07-28 14:59:43.185 UTC [1] LOG got SIGINT, shutting down
2022-07-28 14:59:43.485 UTC [1] LOG server connections dropped, exiting
```

### Integration test

`integration-test/` checks the Kerberos path end to end. It starts a throwaway KDC that issues one-minute tickets, a Postgres that
only accepts GSSAPI logins for the `houston` role, and pgbouncers from the image under test. The pgbouncers run the way the platform
chart runs them: read-only root filesystem with a writable `/tmp`, all capabilities dropped. The tests check that:

- With `server_gssauth_negotiate = allow`, a query through pgbouncer lands on a server connection that Postgres reports as
  GSSAPI-authenticated as `houston@KRB.TEST`. This also holds as an arbitrary UID with GID 0, the way OpenShift runs it.
- Clients log in to pgbouncer with `md5` or SCRAM passwords, and a wrong password is refused.
- With `server_gssauth_negotiate = disable`, the login is refused.
- After its tickets expire, pgbouncer gets new ones from its keytab and still logs in. This test waits about 75 seconds.

CI runs it in the `integration-test` job, and releases wait for it. To run it locally, build the image and point the test at it:

```bash
make build image_name=pgbouncer-krb
ASTRO_IMAGE_NAME=ap-pgbouncer-krb uv run pytest -v pgbouncer-krb/integration-test/test.py
```

`ASTRO_IMAGE_TAG` defaults to `$CIRCLE_SHA1`, then `latest`. Set both variables to test a published image, for example
`ASTRO_IMAGE_NAME=quay.io/astronomer/ap-pgbouncer-krb ASTRO_IMAGE_TAG=1.25.0-6`.
