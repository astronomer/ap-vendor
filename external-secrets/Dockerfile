#
# Copyright 2026 Astronomer Inc.
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

#FROM ghcr.io/external-secrets/external-secrets:2.7.0
#FROM cgr.dev/astronomer.io/external-secrets:2.8.0
#LABEL maintainer="Astronomer <humans@astronomer.io>"

#ARG BUILD_NUMBER=-1
#LABEL io.astronomer.docker=true
#LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ARG GO_VERSION=1.26.4
FROM golang:${GO_VERSION}-alpine3.22 AS build

ENV ESO_DIR=/go/src/github.com/astronomer/external-secrets

ARG GOOS=linux
ARG GOARCH=amd64
ARG GOARM=6
ARG VERSION
ARG REVISION

RUN set -ex \
    && apk add --no-cache make git file

WORKDIR $ESO_DIR

RUN git clone https://github.com/astronomer/external-secrets.git $ESO_DIR && git checkout 80ba47d0f6aa39fcf5b0ecac2cc73985c2fdc97c

RUN go mod download
RUN go build -tags all_providers -o external-secrets main.go

# Final docker image building stage
# https://quay.io/repository/astronomer/ap-base?tab=tags&tag=latest
FROM quay.io/astronomer/ap-base:2026.6.23
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
LABEL maintainer="Astronomer <humans@astronomer.io>"

COPY --from=build /go/src/github.com/astronomer/external-secrets/external-secrets /bin/external-secrets

USER 65534

ENTRYPOINT ["/bin/external-secrets"]
