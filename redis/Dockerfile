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

# https://hub.docker.com/_/redis
FROM redis:6.2.7
LABEL maintainer="Astronomer <humans@astronomer.io>"

# Update packages to solve security vulnerabilities
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get dist-upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Make it possible to override the UID/GID/username of the user running
ARG UID=999
ARG GID=999
# Since username and group name `redis` already exists in base image
ARG USER=redis

# Change gid of a specific group
RUN groupmod -g $GID $UNAME \
  && chgrp $GID /data

RUN usermod -u $UID -g $GID $UNAME

# Adding enough permission for redis to use redis-server service  https://redis.io/docs/manual/persistence/
RUN chown -R $UID:$GID /usr/local/bin/redis*

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# Switching user to redis:999
USER $UNAME
