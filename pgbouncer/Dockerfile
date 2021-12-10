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
# https://quay.io/repository/centerforopenscience/pgbouncer
FROM alpine:3.14
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV PGBOUNCER_VERSION=1.16.0 \
    PGBOUNCER_SHA256=a4a391618bb83caaee2a8cd9653974f4c1b98b95987d5cabbbeb801da6342652

RUN addgroup -S pgbouncer \
    && adduser -D -S -s /sbin/nologin -G pgbouncer pgbouncer \
    && apk add --no-cache --virtual .run-deps \
      c-ares \
      entr \
      libevent \
      libressl

RUN apk add --no-cache --virtual .build-deps \
      build-base \
      autoconf \
      wget \
      c-ares-dev \
      libevent-dev \
      libressl-dev \
    && wget https://pgbouncer.github.io/downloads/files/$PGBOUNCER_VERSION/pgbouncer-$PGBOUNCER_VERSION.tar.gz \
    && echo "$PGBOUNCER_SHA256  /pgbouncer-$PGBOUNCER_VERSION.tar.gz" | sha256sum -c - \
    && tar -xzvf pgbouncer-$PGBOUNCER_VERSION.tar.gz \
    && cd pgbouncer-$PGBOUNCER_VERSION \
    && ./configure --prefix=/usr --disable-debug \
    && make \
    && make install \
    && mkdir /etc/pgbouncer \
    && cp ./etc/pgbouncer.ini /etc/pgbouncer/ \
    && touch /etc/pgbouncer/userlist.txt \
    && sed -i \
      -e "s|logfile = |#logfile = |" \
      -e "s|pidfile = |#pidfile = |" \
      -e "s|listen_addr = .*|listen_addr = 0.0.0.0|" \
      -e "s|auth_type = .*|auth_type = md5|" \
      /etc/pgbouncer/pgbouncer.ini \
    && cd .. \
    && rm pgbouncer-$PGBOUNCER_VERSION.tar.gz \
    && rm -rf pgbouncer-$PGBOUNCER_VERSION \
    && apk del .build-deps
USER pgbouncer
CMD ["pgbouncer", "-u", "pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]

