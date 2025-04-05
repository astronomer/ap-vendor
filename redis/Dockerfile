#
# Copyright 2018 Astronomer Inc.
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

# https://hub.docker.com/r/curlimages/curl/tags
FROM curlimages/curl:latest AS downloader

ENV REDIS_VERSION=7.4.2
ENV REDIS_DOWNLOAD_URL=http://download.redis.io/releases/redis-7.4.2.tar.gz
ENV REDIS_DOWNLOAD_SHA=4ddebbf09061cbb589011786febdb34f29767dd7f89dbe712d2b68e808af6a1f

WORKDIR /tmp

RUN mkdir redis ; curl -fsSL $REDIS_DOWNLOAD_URL -o redis.tar.gz; echo "$REDIS_DOWNLOAD_SHA *redis.tar.gz" | sha256sum -c -;	\
    tar -xzf redis.tar.gz -C redis --strip-components=1; \
    rm redis.tar.gz;

# https://raw.githubusercontent.com/redis/docker-library-redis/refs/heads/master/7.4/debian/Dockerfile
FROM debian:bookworm-slim AS build
LABEL maintainer="Astronomer <humans@astronomer.io>"

COPY --from=downloader /tmp/redis /usr/src/redis
COPY install_packages /usr/local/bin/install_packages
COPY build-redis.sh /usr/local/bin/build-redis.sh

# Make it possible to override the UID/GID/username of the user running
ARG UID=999
ARG GID=999
ARG USER=redis

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN set -eux; \
	groupadd -r -g $GID redis; \
	useradd -r -g redis -u $UID redis

# add tzdata explicitly for https://github.com/docker-library/redis/issues/138 (see also https://bugs.debian.org/837060 and related)
RUN build-redis.sh

FROM debian:bookworm-slim

# Make it possible to override the UID/GID/username of the user running
ARG UID=999
ARG GID=999
ARG USER=redis
ARG BUILD_NUMBER=-1

LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN set -eux; \
	groupadd -r -g $GID redis; \
	useradd -r -g redis -u $UID redis

COPY install_packages /usr/local/bin/install_packages

RUN install_packages ca-certificates dpkg-dev libc6-dev libssl-dev

COPY --from=build /usr/local/bin/redis* /usr/local/bin/
COPY docker-entrypoint.sh /usr/local/bin/

RUN mkdir /data && chown redis:redis /data

VOLUME /data

WORKDIR /data

## Change gid of a specific group
RUN groupmod -g $GID $USER \
  && chgrp $GID /data \
  && usermod -u $UID -g $GID $USER

## Adding enough permission for redis to use redis-server service  https://redis.io/docs/manual/persistence/
RUN chown -R $UID:$GID /usr/local/bin/redis*

## Switching user to redis:999
USER $UID

EXPOSE 6379

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["redis-server"]
