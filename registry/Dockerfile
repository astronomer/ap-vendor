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

# https://console.chainguard.dev/org/astronomer.io/images/organization/image/ap-registry/versions
# Registry image uses sha256 digest to ensure we are using the exact same image as the upstream, which is important for security and stability. The version of the registry image can be found in version.txt, but the sha256 digest must be looked up manually on chainguard.dev.
FROM cgr.dev/astronomer.io/ap-registry@sha256:18f1cb5c3fa1b36861c67f668a50ec6c748d02e8006374716d9a43a0ba8d58fe AS upstream

FROM quay.io/astronomer/ap-base:2026.03.18
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV UPDATE_CA_CERTS=false
ENV OTEL_TRACES_EXPORTER=none

USER 0

# Create registry user and group
RUN addgroup -g 1000 -S registry \
    && adduser -u 1000 -S registry -G registry

RUN set -ex \
    && apk add --no-cache ca-certificates

# Adopt openshift permissions
RUN chown -R 1000:1000 /etc/ssl/ \
    && chown -R 1000:0 /etc/ssl/certs \
    && chmod -R ug+rwx /etc/ssl/certs

COPY --from=upstream --chown=1000:1000 /bin/registry /bin/registry
COPY --chown=1000:1000 ./config-example.yml /etc/docker/registry/config.yml

VOLUME ["/var/lib/registry"]
EXPOSE 5000

COPY --chown=1000:1000 docker-entrypoint.sh /entrypoint.sh

USER 1000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/etc/docker/registry/config.yml"]
