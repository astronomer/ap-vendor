#
# Copyright 2019 Astronomer Inc.
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

# https://www.docker.elastic.co/r/elasticsearch
FROM cgr.dev/astronomer.io/ap-elasticsearch:8.19.23
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER 0

# Remove existing user/group if they exist, then recreate with desired UID/GID
RUN deluser elasticsearch 2>/dev/null || true && \
    delgroup elasticsearch 2>/dev/null || true && \
    addgroup -g 1000 elasticsearch && \
    adduser -D -u 1000 -G elasticsearch -s /bin/sh elasticsearch

# google-api-client ships a trust store, google.jks, that still lists AAA Certificate Services
# (CVE-2026-111943). Drop the affected roots from it in every copy of the jar (PINF-1304).
RUN set -e; \
    for jar in $(find /usr/share/elasticsearch -name 'google-api-client-*.jar'); do \
        tmp=$(mktemp -d); \
        unzip -q "$jar" com/google/api/client/googleapis/google.jks -d "$tmp"; \
        jks="$tmp/com/google/api/client/googleapis/google.jks"; \
        for alias in $(keytool -list -v -keystore "$jks" -storepass notasecret | \
            awk '/^Alias name:/{a=$3} /^Owner:/ && /AAA Certificate Services|emSign|CN=EM (DV|OV|EV|CS)/{print a}'); do \
            keytool -delete -alias "$alias" -keystore "$jks" -storepass notasecret; \
        done; \
        owner=$(stat -c %u:%g "$jar"); mode=$(stat -c %a "$jar"); \
        jar uf "$jar" -C "$tmp" com/google/api/client/googleapis/google.jks; \
        chown "$owner" "$jar"; chmod "$mode" "$jar"; \
        rm -rf "$tmp"; \
    done

USER 1000
