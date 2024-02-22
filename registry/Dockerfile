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
ARG GO_VERSION=1.15
FROM golang:${GO_VERSION}-alpine3.14 AS build

ENV DISTRIBUTION_DIR /go/src/github.com/distribution/distribution
ENV BUILDTAGS include_oss include_gcs

ARG GOOS=linux
ARG GOARCH=amd64
ARG GOARM=6
ARG VERSION
ARG REVISION

RUN set -ex \
    && apk add --no-cache make git file

WORKDIR $DISTRIBUTION_DIR

# this commit includes some important fixes we need to apply:  https://github.com/distribution/distribution/issues/3097 and
# in includes fix of https://github.com/distribution/distribution/issues/625
# since no official release since 2019 o_O
RUN git clone https://github.com/astronomer/distribution.git $DISTRIBUTION_DIR && git checkout 26bdf12d62492d8cb8e8ed98f490ce99f655f343

RUN CGO_ENABLED=0 make PREFIX=/go clean binaries && file ./bin/registry | grep "statically linked"

FROM quay.io/astronomer/ap-base:3.18.6
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
