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
FROM cgr.dev/chainguard/redis:8.0.3-dev
LABEL maintainer="Astronomer <humans@astronomer.io>"

# Make it possible to override the UID/GID/username of the user running
ARG UID=999
ARG GID=999
ARG USER=redis

## Modify redis uid/gid to match our custom values
USER root
RUN apk update && \
    apk add shadow && \
    usermod -u $UID $USER && \
    groupmod -g $GID $USER && \
    chown -R $USER:$USER /data /home/redis /home/$USER && \
    apk del shadow && \
    rm -rf /var/cache/apk/*

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# Switch to the newly updated user
USER $USER
