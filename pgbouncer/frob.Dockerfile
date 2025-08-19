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


##### Three-stage build
#  common--+                       common has only stuff you need at both build and run
#          |
#          +----build              build produces the binary
#          |
#          +----main               runs the binary


##### FIRST STAGE: common - stuff needed at both build and run time

FROM quay.io/astronomer/ap-base:3.21.3-4 as common
RUN addgroup -S pgbouncer \
    && adduser -D -S -s /sbin/nologin -G pgbouncer pgbouncer \
    && apk add --no-cache --virtual .run-deps \
      c-ares \
      entr \
      krb5 \
      krb5-dev \
      krb5-pkinit \
      libevent \
      libressl

###### SECOND STAGE: build
# Weare not ready to pin yet
ENV PGBOUNCER_SHA256_CHECKSUM c1cbecdd469327f132005a0ba5a965b710362abe
FROM common as build
RUN apk add --no-cache --virtual .build-deps \
      bash \
      autoconf \
      automake \
      build-base \
      c-ares-dev \
      git \
      libevent-dev \
      libtool \
      openssl-dev \
      pkgconf \
      wget \
      pandoc \
# shallow-fetch only the single commit we care about
RUN
    && mkdir /pgbouncer \
    && cd /pgbouncer \
    && git init \
    && git remote add origin https://github.com/rob-1126/pgbouncer.git \
    && git fetch --depth 1 origin $PGBOUNCER_COMMIT \
    && git checkout FETCH_HEAD \
    && git submodule init \
    && git submodule update \
    # pull in Kerberos compile- and link-flags…
    && export CPPFLAGS="$(pkgconf --cflags gssapi_krb5)" \
    && export LDFLAGS="$(pkgconf --libs gssapi_krb5)" \
    && export LIBS="-lgssapi_krb5 -lkrb5 -lk5crypto -lcom_err" \
    && ./autogen.sh \
    && ./configure --prefix=/bar --disable-debug --with-gss --with-openssl --with-libevent \
    && make \
    && make install
