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

# https://hub.docker.com/r/jbub/pgbouncer_exporter
FROM cgr.dev/astronomer.io/prometheus-pgbouncer-exporter:0.12.1-dev AS upstream

FROM quay.io/astronomer/ap-base:2026.6.23

LABEL maintainer="Astronomer <humans@astronomer.io>"

# Make it possible to override the UID/GID/username of the user running
ARG UID=1000
ARG GID=1001
ARG BUILD_NUMBER=-1
ARG USER=pgexporter
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root

COPY --from=upstream /bin/pgbouncer_exporter /bin

RUN apk upgrade --no-cache

RUN addgroup -g $GID -S $USER \
    && adduser -D -S -s /sbin/nologin -G $USER -u $UID $USER

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER $UID

ENTRYPOINT ["/entrypoint.sh"]
