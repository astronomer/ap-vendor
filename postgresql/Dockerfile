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

# https://hub.docker.com/r/bitnami/postgresql/tags/

FROM cgr.dev/astronomer.io/ap-postgres:17-dev
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV POSTGRESQL_MAX_CONNECTIONS=200

USER root

# Update packages
RUN apk update && apk upgrade && \
    rm -rf /var/cache/apk/*

# Remove existing postgres user/group and recreate with UID/GID 1001
RUN deluser postgres || true && \
    delgroup postgres || true && \
    addgroup -g 1001 postgres && \
    adduser -u 1001 -G postgres -D -S -h /var/lib/postgresql postgres

# Create the /bitnami/postgresql directory structure for compatibility with tests
RUN mkdir -p /bitnami/postgresql && \
    chown -R 1001:1001 /bitnami/postgresql

# Also ensure the standard PostgreSQL data directory has correct permissions
RUN mkdir -p /var/lib/postgresql/data && \
    chown -R 1001:1001 /var/lib/postgresql

USER 1001
