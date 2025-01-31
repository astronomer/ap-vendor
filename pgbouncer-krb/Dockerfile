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

FROM quay.io/astronomer/ap-base:3.20.3-1
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV REALM ${REALM:-EXAMPLE.COM}
ENV KADMIN_PRINCIPAL ${KADMIN_PRINCIPAL:-kadmin/admin}
ENV KADMIN_PASSWORD ${KADMIN_PASSWORD:-postgres}

RUN addgroup -S pgbouncer \
    && adduser -D -S -s /sbin/nologin -G pgbouncer pgbouncer \
    && apk add --no-cache --virtual .run-deps \
      bash \
      c-ares \
      entr \
      krb5 \
      krb5-dev \
      krb5-pkinit \
      libevent \
      libressl

RUN apk add --no-cache --virtual .build-deps \
      autoconf \
      automake \
      build-base \
      c-ares-dev \
      git \
      libevent-dev \
      libtool \
      openssl-dev \
      wget \
    && wget "https://github.com/jgm/pandoc/releases/download/2.18/pandoc-2.18-linux-amd64.tar.gz" \
    && tar xvzf pandoc-2.18-linux-amd64.tar.gz --strip-components 1 -C /usr/local \
    && git clone https://github.com/astronomer/pgbouncer.git --single-branch --branch cory/gss-authentication \
    && cd /pgbouncer; \
       git submodule init; \
       git submodule update \
    && ./autogen.sh \
    && ./configure --prefix=/usr --with-server-gssenc \
    && make \
    && make install \
    && mkdir /etc/pgbouncer \
    && touch /etc/pgbouncer/userlist.txt \
    && cd .. \
    && rm -rf /pgbouncer* \
    && apk del .build-deps

RUN chown -R pgbouncer /etc/krb5.conf /etc/pgbouncer/

COPY entrypoint.sh /entrypoint.sh

USER pgbouncer

ENTRYPOINT ["/entrypoint.sh"]
CMD ["pgbouncer", "-u", "pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]
