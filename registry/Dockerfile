# syntax=docker/dockerfile:1
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

ARG GO_VERSION=1.19
ARG ALPINE_VERSION=3.18
FROM golang:${GO_VERSION}-alpine${ALPINE_VERSION} AS base
RUN apk add --no-cache bash coreutils file git make
ENV GO111MODULE=auto
ENV CGO_ENABLED=0
ENV DISTRIBUTION_DIR /go/src/github.com/docker/distribution
WORKDIR $DISTRIBUTION_DIR
RUN git clone https://github.com/distribution/distribution.git $DISTRIBUTION_DIR && git checkout tags/v2.8.2
COPY parser.go $DISTRIBUTION_DIR/configuration/parser.go

# This step is required to generate build config
FROM base AS version
ARG PKG="github.com/docker/distribution"
ENV REGISTRY_VERSION 2.8.2
RUN --mount=target=. \
  VERSION=$(git describe --match 'v[0-9]*' --dirty='.m' --always --tags) REVISION=$(git rev-parse HEAD)$(if ! git diff --no-ext-diff --quiet --exit-code; then echo .m; fi); \
  echo "-X ${PKG}/version.Version=${REGISTRY_VERSION} -X ${PKG}/version.Revision=${REVISION} -X ${PKG}/version.Package=${PKG}" | tee /tmp/.ldflags; \
  echo -n "${VERSION}" | tee /tmp/.version;

FROM base AS build
ENV DISTRIBUTION_DIR /go/src/github.com/distribution/distribution
ENV BUILDTAGS include_oss include_gcs

ARG GOOS=linux
ARG GOARCH=amd64
ARG GOARM=6
ARG VERSION
ARG REVISION
RUN CGO_ENABLED=0 make PREFIX=/go clean binaries && file ./bin/registry | grep "statically linked"

FROM quay.io/astronomer/ap-base:3.18.3
LABEL maintainer="Astronomer <humans@astronomer.io>"
ENV DISTRIBUTION_DIR /go/src/github.com/distribution/distribution
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

## Create registry user and group
RUN addgroup -g 1000 -S registry \
    && adduser -u 1000 -S registry -G registry

RUN set -ex \
    && apk add --no-cache ca-certificates

COPY --from=build --chown=1000:1000 /go/src/github.com/docker/distribution/bin/registry /bin/registry
COPY --chown=1000:1000 ./config-example.yml /etc/docker/registry/config.yml

VOLUME ["/var/lib/registry"]
EXPOSE 5000

COPY --chown=1000:1000 docker-entrypoint.sh /entrypoint.sh

USER 1000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/etc/docker/registry/config.yml"]
