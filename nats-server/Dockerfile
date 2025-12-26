#
# Copyright 2016 Astronomer Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License") ;
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

# https://console.chainguard.dev/org/astronomer.io/images/organization?query=nats
FROM cgr.dev/astronomer.io/nats:v2.12.1 AS upstream

FROM quay.io/astronomer/ap-base:2025.12.24

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root

RUN addgroup -g 1000 -S nats \
	&& adduser -u 1000 -S nats -G nats

COPY --from=upstream --chown=1000:1000 /usr/bin/nats-server /usr/local/bin/nats-server
COPY --chown=1000:1000 nats-server.conf /etc/nats/nats-server.conf
COPY --chown=1000:1000 docker-entrypoint.sh /usr/local/bin

USER 1000

EXPOSE 4222 8222 6222

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["nats-server", "--config", "/etc/nats/nats-server.conf"]
