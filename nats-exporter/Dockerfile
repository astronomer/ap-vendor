#
# Copyright 2020 Astronomer Inc.
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

# Golang binary building stage
ARG GO_VERSION=1.15

FROM golang:${GO_VERSION}-alpine3.14 AS build

RUN set -ex \
    && apk add --no-cache make git file

WORKDIR $GOPATH/src/github.com/nats-io/prometheus-nats-exporter

RUN git clone --branch v0.9.1 https://github.com/nats-io/prometheus-nats-exporter.git .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -v -a -tags netgo -installsuffix netgo -ldflags "-s -w"

# Final docker image building stage
FROM alpine:3.15

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
LABEL maintainer="Astronomer <humans@astronomer.io>"

# Create prometheus-nats-exporter user and group
RUN addgroup -g 1000 -S prometheus-nats-exporter \
    && adduser -u 1000 -S prometheus-nats-exporter -G prometheus-nats-exporter

COPY --from=build --chown=1000:1000 /go/src/github.com/nats-io/prometheus-nats-exporter/prometheus-nats-exporter /prometheus-nats-exporter

EXPOSE 7777

USER prometheus-nats-exporter

ENTRYPOINT ["/prometheus-nats-exporter"]

CMD ["--help"]
