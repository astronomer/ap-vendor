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

ARG GO_VERSION=1.15

FROM golang:${GO_VERSION}-alpine3.12 AS build

ENV DISTRIBUTION_DIR /go/src/github.com/prometheus/blackbox_exporter
ENV BUILDTAGS include_oss include_gcs

ARG GOOS=linux
ARG GOARCH=amd64
ARG GOARM=6
ARG VERSION
ARG REVISION

RUN set -ex \
    && apk add --no-cache make git curl

WORKDIR $DISTRIBUTION_DIR

RUN git clone https://github.com/prometheus/blackbox_exporter $DISTRIBUTION_DIR && git checkout v0.19.0

RUN CGO_ENABLED=0 make build

FROM quay.io/astronomer/ap-base:3.13.5
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# Create blackbox-exporter user and group
RUN addgroup -g 1000 -S blackbox-exporter \
    && adduser -u 1000 -S blackbox-exporter -G blackbox-exporter

RUN set -ex \
    && apk add --no-cache ca-certificates

COPY --from=build --chown=1000:1000 /go/src/github.com/prometheus/blackbox_exporter/blackbox_exporter /usr/local/bin
COPY --from=build --chown=1000:1000 /go/src/github.com/prometheus/blackbox_exporter/blackbox.yml /etc/blackbox_exporter/blackbox.yml
USER blackbox-exporter

EXPOSE      9115

ENTRYPOINT  [ "blackbox_exporter" ]
CMD         [ "--config.file=/etc/blackbox_exporter/blackbox.yml" ]
