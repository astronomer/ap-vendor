## Pgbouncer with custom gss support

### Environment variables

```
# Manage to gnerate example of /etc/krb5
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
