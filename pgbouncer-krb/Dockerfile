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

##### FIRST STAGE: common - stuff needed at both build and run time

FROM quay.io/astronomer/ap-base:3.21.3-4 AS common

RUN apk add --no-cache --virtual .run-deps \
      c-ares \
      entr \
      krb5 \
      krb5-dev \
      krb5-pkinit \
      libevent \
      libressl

###### SECOND STAGE: build
FROM common AS build

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
      pandoc
    # shallow-fetch only the single commit we care about
RUN mkdir /build \
    && cd /build \
    && git init \
    && git remote add origin https://github.com/astronomer/pgbouncer.git \
    && git fetch \
    && git checkout kerberos-support \
    && git submodule init \
    && git submodule update \
    # pull in Kerberos compile- and link-flags…
    && export CPPFLAGS="$(pkgconf --cflags gssapi)" \
    && export LDFLAGS="$(pkgconf --libs gssapi)" \
    && export LIBS="-lgssapi_krb5 -lkrb5 -lk5crypto -lcom_err" \
    && ./autogen.sh \
    && ./configure --prefix=/usr --disable-debug --with-gss --with-openssl \
    && make \
    && make install
# construct a modified /build/pgbouncer.ini
RUN cd /build \
    && cp etc/pgbouncer.ini modified-pgbouncer.ini \
    && sed -i \
      -e "s|logfile = |#logfile = |" \
      -e "s|pidfile = |#pidfile = |" \
      -e "s|listen_addr = .*|listen_addr = 0.0.0.0|" \
      -e "s|auth_type = .*|auth_type = md5|" \
      modified-pgbouncer.ini

##### THIRD STAGE: main

FROM quay.io/astronomer/ap-base:2025.12.03 AS main

LABEL maintainer="Astronomer <humans@astronomer.io>"

# Make it possible to override the UID/GID/username of the user running
ARG UID=1000
ARG GID=1001
ARG BUILD_NUMBER=-1
ARG USER=pgbouncer

LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root

RUN addgroup -g $GID -S $USER \
  && adduser -D -S -s /sbin/nologin -G $USER -u $UID $USER \
  && mkdir /etc/pgbouncer \
  && touch /etc/pgbouncer/userlist.txt

# copy over build output
COPY --from=build /usr/bin/pgbouncer /usr/bin/pgbouncer
COPY --from=build /usr/share/doc/pgbouncer /usr/share/doc
COPY --from=build /build/modified-pgbouncer.ini /etc/pgbouncer/pgbouncer.ini
COPY docker-entrypoint.sh docker-entrypoint.sh

# setup user, entrypoint, and cmd
USER $UID
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]
