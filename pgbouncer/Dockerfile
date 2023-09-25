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
FROM quay.io/astronomer/ap-base:3.18.3
LABEL maintainer="Astronomer <humans@astronomer.io>"

# Make it possible to override the UID/GID/username of the user running
ARG UID=1000
ARG GID=1001
ARG BUILD_NUMBER=-1
ARG USER=pgbouncer

LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV PGBOUNCER_VERSION=1.20.1 \
  PGBOUNCER_SHA256=24992cf557d73426d7048698dffc7b019e6364d4d8757ae2cf5e2471286a2088

RUN addgroup -g $GID -S $USER \
  && adduser -D -S -s /sbin/nologin -G $USER -u $UID $USER \
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
  openssl-dev \
  && wget https://www.pgbouncer.org/downloads/files/$PGBOUNCER_VERSION/pgbouncer-$PGBOUNCER_VERSION.tar.gz \
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
COPY ./docker-entrypoint.sh docker-entrypoint.sh
USER $UID
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]
