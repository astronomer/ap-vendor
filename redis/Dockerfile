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
FROM cgr.dev/astronomer.io/redis:8.10.2-dev
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

# ca-certificates-bundle 20260909-r3 drops the eMudhra-compromised root (PINF-1304); remove once the base image ships it.
COPY --from=cgr.dev/chainguard/static:latest@sha256:17367e4d3ae2b46c3290858e483fac09be085c92b372360fe3bf6a6150848fde \
    /etc/ssl/certs/ca-certificates.crt \
    /etc/ssl/certs/.ca-certificates.crt.sha256 \
    /etc/ssl/certs/

# Switch to the newly updated user
USER $USER
