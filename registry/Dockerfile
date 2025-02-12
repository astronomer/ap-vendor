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
ARG GO_VERSION=1.22.10
FROM golang:${GO_VERSION}-alpine3.20 AS build

ENV DISTRIBUTION_DIR /go/src/github.com/distribution/distribution
ENV BUILDTAGS include_oss include_gcs

ARG GOOS=linux
ARG GOARCH=amd64
ARG GOARM=7  # WTF is this and why is it needed? https://go.dev/wiki/GoArm
ARG VERSION
ARG REVISION

RUN set -ex \
    && apk add --no-cache make git file

WORKDIR $DISTRIBUTION_DIR

# https://github.com/distribution/distribution/releases
ENV REGISTRY_VERSION 2.8.3

RUN set -eux ; \
	url="https://github.com/distribution/distribution/releases/download/v${REGISTRY_VERSION}/registry_${REGISTRY_VERSION}_linux_amd64.tar.gz"; \
	sha256="b68ffb849bcdb49639dc91ba97baba6618346f95fedc0fcc94871b31d515d205" ; \
	wget -O registry.tar.gz "${url}" ; \
	echo "$sha256 *registry.tar.gz" | sha256sum -c -; \
	tar --extract --verbose --file registry.tar.gz --directory /bin/ registry; \
	rm registry.tar.gz; \
	registry --version

RUN CGO_ENABLED=0 make PREFIX=/go clean binaries && file ./bin/registry | grep "statically linked"

FROM quay.io/astronomer/ap-base:3.20.5
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV UPDATE_CA_CERTS false

# Create registry user and group
RUN addgroup -g 1000 -S registry \
    && adduser -u 1000 -S registry -G registry

RUN set -ex \
    && apk add --no-cache ca-certificates

# Adopt openshift permissions
RUN chown -R 1000:1000 /etc/ssl/ \
    && chown -R 1000:0 /etc/ssl/certs \
    && chmod -R ug+rwx /etc/ssl/certs

COPY --from=build --chown=1000:1000 /go/src/github.com/distribution/distribution/bin/registry /bin/registry
COPY --chown=1000:1000 ./config-example.yml /etc/docker/registry/config.yml

VOLUME ["/var/lib/registry"]
EXPOSE 5000

COPY --chown=1000:1000 docker-entrypoint.sh /entrypoint.sh

USER 1000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/etc/docker/registry/config.yml"]
