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

# https://console.chainguard.dev/org/astronomer.io/images/organization/image/ap-blackbox-exporter/versions
FROM cgr.dev/astronomer.io/ap-blackbox-exporter:0.29.0 AS upstream

# https://quay.io/repository/astronomer/ap-base?tab=tags
FROM quay.io/astronomer/ap-base:2026.10.19
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root

# Create blackbox-exporter user and group
RUN addgroup -g 1000 -S blackbox-exporter \
    && adduser -u 1000 -S blackbox-exporter -G blackbox-exporter

RUN set -ex \
    && apk add --no-cache ca-certificates

COPY --from=upstream --chown=1000:1000 /usr/bin/blackbox_exporter /usr/local/bin/blackbox_exporter
COPY --from=upstream --chown=1000:1000 /etc/blackbox_exporter/config.yml /etc/blackbox_exporter/blackbox.yml
USER 1000

EXPOSE      9115

ENTRYPOINT  [ "blackbox_exporter" ]
CMD         [ "--config.file=/etc/blackbox_exporter/blackbox.yml" ]
