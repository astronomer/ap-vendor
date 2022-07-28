#!/bin/sh
# Based on https://github.com/edoburu/docker-pgbouncer/blob/860ed3643/entrypoint.sh
# but pass all shellchecks

set -ex


if [ -z "$GENERATE_KRB5_CONFIG" ]
then
  echo "skipping generating /etc/krb5.conf"
else
  echo "==================================================================================="
  echo "==== Kerberos Client =============================================================="
  echo "==================================================================================="
  KADMIN_PRINCIPAL_FULL=$KADMIN_PRINCIPAL@$REALM

  echo "REALM: $REALM"
  echo "KADMIN_PRINCIPAL_FULL: $KADMIN_PRINCIPAL_FULL"
  echo "KADMIN_PASSWORD: $KADMIN_PASSWORD"
  echo ""

  kadminCommand() {
      kadmin -p "$KADMIN_PRINCIPAL_FULL" -w "$KADMIN_PASSWORD" -q "$1"
  }

  echo "==================================================================================="
  echo "==== /etc/krb5.conf ==============================================================="
  echo "==================================================================================="
  whoami
  ls -la /etc/krb5*
  tee /etc/krb5.conf <<EOF
[libdefaults]
  rdns = false
  default_realm = $REALM
[realms]
  $REALM = {
    kdc = kdc-kadmin
    admin_server = kdc-kadmin
  }
EOF
  echo ""

  echo "==================================================================================="
  echo "==== Testing ======================================================================"
  echo "==================================================================================="
  until kadminCommand "list_principals $KADMIN_PRINCIPAL_FULL"; do
    >&2 echo "KDC is unavailable - sleeping 1 sec"
    sleep 1
  done
  echo "KDC and Kadmin are operational"
  echo ""
fi

# Here are some parameters. See all on
# https://pgbouncer.github.io/config.html

PG_CONFIG_DIR=/etc/pgbouncer

if [ -n "$DATABASE_URL" ]; then
  # Thanks to https://stackoverflow.com/a/17287984/146289

  # Allow to pass values like dj-database-url / django-environ accept
  proto="$(echo "$DATABASE_URL" | grep :// | sed -e's,^\(.*://\).*,\1,g')"
  url="$(echo "$DATABASE_URL" | sed -e s,"$proto",,g)"

  # extract the user and password (if any)
  userpass=$(echo "$url" | grep @ | sed -r 's/^(.*)@([^@]*)$/\1/')
  DB_PASSWORD="$(echo "$userpass" | grep : | cut -d: -f2)"
  if [ -n "$DB_PASSWORD" ]; then
    DB_USER=$(echo "$userpass" | grep : | cut -d: -f1)
  else
    DB_USER=$userpass
  fi

  # extract the host -- updated
  hostport=$(echo "$url" | sed -e s,"$userpass"@,,g | cut -d/ -f1)
  port=$(echo "$hostport" | grep : | cut -d: -f2)
  if [ -n "$port" ]; then
    DB_HOST=$(echo "$hostport" | grep : | cut -d: -f1)
      DB_PORT=$port
  else
      DB_HOST=$hostport
  fi

  DB_NAME="$(echo "$url" | grep / | cut -d/ -f2-)"
fi

# Write the password with MD5 encryption, to avoid printing it during startup.
# Notice that `docker inspect` will show unencrypted env variables.
_AUTH_FILE="${AUTH_FILE:-$PG_CONFIG_DIR/userlist.txt}"

# Workaround userlist.txt missing issue
# https://github.com/edoburu/docker-pgbouncer/issues/33
if [ ! -e "${_AUTH_FILE}" ]; then
  touch "${_AUTH_FILE}"
fi
# shellcheck disable=SC2166
if [ -n "$DB_USER" -a -n "$DB_PASSWORD" -a -e "${_AUTH_FILE}" ] && ! grep -q "^\"$DB_USER\"" "${_AUTH_FILE}"; then
  if [ "$AUTH_TYPE" != "plain" ]; then
     pass="md5$(echo "$DB_PASSWORD$DB_USER" | md5sum | cut -f 1 -d ' ')"
  else
     pass="$DB_PASSWORD"
  fi
  echo "\"$DB_USER\" \"$pass\"" >> ${PG_CONFIG_DIR}/userlist.txt
  echo "Wrote authentication credentials to ${PG_CONFIG_DIR}/userlist.txt"
fi

if [ ! -f ${PG_CONFIG_DIR}/pgbouncer.ini ]; then
  echo "Create pgbouncer config in ${PG_CONFIG_DIR}"

# Config file is in "ini" format. Section names are between "[" and "]".
# Lines starting with ";" or "#" are taken as comments and ignored.
# The characters ";" and "#" are not recognized when they appear later in the line.
  cat <<EOF > "${PG_CONFIG_DIR}/pgbouncer.ini"
################## Auto generated ##################
[databases]
${DB_NAME:-*} = host=${DB_HOST:?"Setup pgbouncer config error! You must set DB_HOST env"}
port=${DB_PORT:-5432} user=${DB_USER:-postgres}
${CLIENT_ENCODING:+client_encoding = ${CLIENT_ENCODING}}
[pgbouncer]
listen_addr = ${LISTEN_ADDR:-0.0.0.0}
listen_port = ${LISTEN_PORT:-5432}
unix_socket_dir =
user = postgres
auth_file = ${AUTH_FILE:-$PG_CONFIG_DIR/userlist.txt}
${AUTH_HBA_FILE:+auth_hba_file = ${AUTH_HBA_FILE}}
auth_type = ${AUTH_TYPE:-md5}
${AUTH_USER:+auth_user = ${AUTH_USER}}
${AUTH_QUERY:+auth_query = ${AUTH_QUERY}}
${POOL_MODE:+pool_mode = ${POOL_MODE}}
${MAX_CLIENT_CONN:+max_client_conn = ${MAX_CLIENT_CONN}}
${DEFAULT_POOL_SIZE:+default_pool_size = ${DEFAULT_POOL_SIZE}}
${MIN_POOL_SIZE:+min_pool_size = ${MIN_POOL_SIZE}}
${RESERVE_POOL_SIZE:+reserve_pool_size = ${RESERVE_POOL_SIZE}}
${RESERVE_POOL_TIMEOUT:+reserve_pool_timeout = ${RESERVE_POOL_TIMEOUT}}
${MAX_DB_CONNECTIONS:+max_db_connections = ${MAX_DB_CONNECTIONS}}
${MAX_USER_CONNECTIONS:+max_user_connections = ${MAX_USER_CONNECTIONS}}
${SERVER_ROUND_ROBIN:+server_round_robin = ${SERVER_ROUND_ROBIN}}
ignore_startup_parameters = ${IGNORE_STARTUP_PARAMETERS:-extra_float_digits}
${DISABLE_PQEXEC:+disable_pqexec = ${DISABLE_PQEXEC}}
${APPLICATION_NAME_ADD_HOST:+application_name_add_host = ${APPLICATION_NAME_ADD_HOST}}
# Log settings
${LOG_CONNECTIONS:+log_connections = ${LOG_CONNECTIONS}}
${LOG_DISCONNECTIONS:+log_disconnections = ${LOG_DISCONNECTIONS}}
${LOG_POOLER_ERRORS:+log_pooler_errors = ${LOG_POOLER_ERRORS}}
${LOG_STATS:+log_stats = ${LOG_STATS}}
${STATS_PERIOD:+stats_period = ${STATS_PERIOD}}
${VERBOSE:+verbose = ${VERBOSE}}
admin_users = ${ADMIN_USERS:-postgres}
${STATS_USERS:+stats_users = ${STATS_USERS}}
# Connection sanity checks, timeouts
${SERVER_RESET_QUERY:+server_reset_query = ${SERVER_RESET_QUERY}}
${SERVER_RESET_QUERY_ALWAYS:+server_reset_query_always = ${SERVER_RESET_QUERY_ALWAYS}}
${SERVER_CHECK_DELAY:+server_check_delay = ${SERVER_CHECK_DELAY}}
${SERVER_CHECK_QUERY:+server_check_query = ${SERVER_CHECK_QUERY}}
${SERVER_LIFETIME:+server_lifetime = ${SERVER_LIFETIME}}
${SERVER_IDLE_TIMEOUT:+server_idle_timeout = ${SERVER_IDLE_TIMEOUT}}
${SERVER_CONNECT_TIMEOUT:+server_connect_timeout = ${SERVER_CONNECT_TIMEOUT}}
${SERVER_LOGIN_RETRY:+server_login_retry = ${SERVER_LOGIN_RETRY}}
${CLIENT_LOGIN_TIMEOUT:+client_login_timeout = ${CLIENT_LOGIN_TIMEOUT}}
${AUTODB_IDLE_TIMEOUT:+autodb_idle_timeout = ${AUTODB_IDLE_TIMEOUT}}
${DNS_MAX_TTL:+dns_max_ttl = ${DNS_MAX_TTL}}
${DNS_NXDOMAIN_TTL:+dns_nxdomain_ttl = ${DNS_NXDOMAIN_TTL}}
# TLS settings
${CLIENT_TLS_SSLMODE:+client_tls_sslmode = ${CLIENT_TLS_SSLMODE}}
${CLIENT_TLS_KEY_FILE:+client_tls_key_file = ${CLIENT_TLS_KEY_FILE}}
${CLIENT_TLS_CERT_FILE:+client_tls_cert_file = ${CLIENT_TLS_CERT_FILE}}
${CLIENT_TLS_CA_FILE:+client_tls_ca_file = ${CLIENT_TLS_CA_FILE}}
${CLIENT_TLS_PROTOCOLS:+client_tls_protocols = ${CLIENT_TLS_PROTOCOLS}}
${CLIENT_TLS_CIPHERS:+client_tls_ciphers = ${CLIENT_TLS_CIPHERS}}
${CLIENT_TLS_ECDHCURVE:+client_tls_ecdhcurve = ${CLIENT_TLS_ECDHCURVE}}
${CLIENT_TLS_DHEPARAMS:+client_tls_dheparams = ${CLIENT_TLS_DHEPARAMS}}
${SERVER_TLS_SSLMODE:+server_tls_sslmode = ${SERVER_TLS_SSLMODE}}
${SERVER_TLS_CA_FILE:+server_tls_ca_file = ${SERVER_TLS_CA_FILE}}
${SERVER_TLS_KEY_FILE:+server_tls_key_file = ${SERVER_TLS_KEY_FILE}}
${SERVER_TLS_CERT_FILE:+server_tls_cert_file = ${SERVER_TLS_CERT_FILE}}
${SERVER_TLS_PROTOCOLS:+server_tls_protocols = ${SERVER_TLS_PROTOCOLS}}
${SERVER_TLS_CIPHERS:+server_tls_ciphers = ${SERVER_TLS_CIPHERS}}
# Dangerous timeouts
${QUERY_TIMEOUT:+query_timeout = ${QUERY_TIMEOUT}}
${QUERY_WAIT_TIMEOUT:+query_wait_timeout = ${QUERY_WAIT_TIMEOUT}}
${CLIENT_IDLE_TIMEOUT:+client_idle_timeout = ${CLIENT_IDLE_TIMEOUT}}
${IDLE_TRANSACTION_TIMEOUT:+idle_transaction_timeout = ${IDLE_TRANSACTION_TIMEOUT}}
${PKT_BUF:+pkt_buf = ${PKT_BUF}}
${MAX_PACKET_SIZE:+max_packet_size = ${MAX_PACKET_SIZE}}
${LISTEN_BACKLOG:+listen_backlog = ${LISTEN_BACKLOG}}
${SBUF_LOOPCNT:+sbuf_loopcnt = ${SBUF_LOOPCNT}}
${SUSPEND_TIMEOUT:+suspend_timeout = ${SUSPEND_TIMEOUT}}
${TCP_DEFER_ACCEPT:+tcp_defer_accept = ${TCP_DEFER_ACCEPT}}
${TCP_KEEPALIVE:+tcp_keepalive = ${TCP_KEEPALIVE}}
${TCP_KEEPCNT:+tcp_keepcnt = ${TCP_KEEPCNT}}
${TCP_KEEPIDLE:+tcp_keepidle = ${TCP_KEEPIDLE}}
${TCP_KEEPINTVL:+tcp_keepintvl = ${TCP_KEEPINTVL}}
${TCP_USER_TIMEOUT:+tcp_user_timeout = ${TCP_USER_TIMEOUT}}
${SERVER_GSSENCMODE:+server_gssencmode = ${SERVER_GSSENCMODE}}
# Kerberos
# ${KRB_SERVER_KEYFILE:+krb_server_keyfile = ${KRB_SERVER_KEYFILE}}
################## end file ##################
EOF

cat ${PG_CONFIG_DIR}/pgbouncer.ini
echo "Starting $*..."
fi

exec "$@"
