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
FROM quay.io/astronomer/ap-base:3.15.4
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV PGBOUNCER_VERSION=1.17.0 \
    PGBOUNCER_SHA256=657309b7bc5c7a85cbf70a9a441b535f7824123081eabb7ba86d00349a256e23

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
      git \
      c-ares-dev \
      libevent-dev \
      libressl-dev \
      openssl-dev \
      libtool \
      automake \
    && wget "https://github.com/jgm/pandoc/releases/download/2.18/pandoc-2.18-linux-amd64.tar.gz" \
    && tar xvzf pandoc-2.18-linux-amd64.tar.gz --strip-components 1 -C /usr/local \
    && git clone https://github.com/astronomer/pgbouncer.git /tmp/pgbouncer; \
       cd /tmp/pgbouncer; \
       git checkout 9a346b0e451d842d7202abc3eccf0ff5a66b2dd6; \
       git submodule init; \
       git submodule update \
    && cd /tmp/pgbouncer && ./autogen.sh \
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
    && rm -rf pgbouncer \
    && apk del .build-deps
# USER pgbouncer
# CMD ["pgbouncer", "-u", "pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]

