#
# Copyright 2016 Astronomer Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# https://github.com/CenterForOpenScience/docker-library/blob/master/pgbouncer/Dockerfile
FROM quay.io/astronomer/ap-base:3.15.4
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV REALM ${REALM:-EXAMPLE.COM}
ENV KADMIN_PRINCIPAL ${KADMIN_PRINCIPAL:-kadmin/admin}
ENV KADMIN_PASSWORD ${KADMIN_PASSWORD:-MITiys4K5}

RUN apk add --no-cache --virtual .run-deps \
      c-ares \
      entr \
      libevent \
      libressl \
      krb5 \
      krb5-dev \
      bash


RUN apk add --no-cache --virtual .build-deps \
      build-base \
      autoconf \
      wget \
      git \
      c-ares-dev \
      libevent-dev \
      libressl-dev \
      openssl-dev \
      libtool \
      automake \
    && wget "https://github.com/jgm/pandoc/releases/download/2.18/pandoc-2.18-linux-amd64.tar.gz" \
    && tar xvzf pandoc-2.18-linux-amd64.tar.gz --strip-components 1 -C /usr/local \
    && git clone https://github.com/astronomer/pgbouncer.git --single-branch --branch cory/gss-authentication /tmp/pgbouncer

RUN cd /tmp/pgbouncer; \
       git submodule init; \
       git submodule update \
    && cd /tmp/pgbouncer && ./autogen.sh \
    && ./configure --prefix=/usr --with-server-gssenc \
    && make && \
    # Manual install
    cp pgbouncer /usr/bin && \
    mkdir -p /etc/pgbouncer /var/log/pgbouncer /var/run/pgbouncer && \
    # cp ./pgbouncer.ini /etc/pgbouncer/pgbouncer.ini && \
    # cp ./userlist.txt /etc/pgbouncer/userlist.txt && \
    # entrypoint installs the configuration, allow to write as postgres user
    addgroup -g 70 -S pgbouncer 2>/dev/null && \
    adduser -u 70 -S -D -H -h /var/lib/postgresql -g "Postgres user" -s /bin/sh -G pgbouncer pgbouncer 2>/dev/null && \
    chown -R pgbouncer /var/run/pgbouncer /etc/pgbouncer && \
    # Cleanupc)
    cd /tmp && \
    rm -rf /tmp/pgbouncer*  && \
    apk del .build-deps

COPY pgbouncer.ini users.txt /etc/pgbouncer
COPY init-script.sh configureKerberosClient.sh /tmp/
CMD /tmp/init-script.sh
