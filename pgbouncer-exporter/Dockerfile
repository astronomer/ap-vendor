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
# we have switched to our own fork of the pgbouncer exporter to update golang version
ARG GO_VERSION=1.21

FROM golang:${GO_VERSION}-alpine3.18 AS build

ENV DISTRIBUTION_DIR /go/src/github.com/astronomer/pgbouncer_exporter

ARG GOOS=linux
ARG GOARCH=amd64
ARG GOARM=6
ARG VERSION
ARG REVISION

RUN set -ex \
    && apk add --no-cache make git curl

WORKDIR $DISTRIBUTION_DIR

RUN git clone https://github.com/astronomer/pgbouncer_exporter $DISTRIBUTION_DIR && git checkout f6cf4391e416db23c1ca61c67fabdeebbc1258f1

RUN make build_linux

FROM quay.io/astronomer/ap-base:3.18.7-1

LABEL maintainer="Astronomer <humans@astronomer.io>"
ENV DISTRIBUTION_DIR /go/src/github.com/astronomer/pgbouncer_exporter
# Make it possible to override the UID/GID/username of the user running
ARG UID=1000
ARG GID=1001
ARG BUILD_NUMBER=-1
ARG USER=pgexporter
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

COPY --from=build $DISTRIBUTION_DIR/pgbouncer_exporter /bin

RUN addgroup -g $GID -S $USER \
    && adduser -D -S -s /sbin/nologin -G $USER -u $UID $USER
USER $UID

ENTRYPOINT ["pgbouncer_exporter"]
CMD ["server"]
