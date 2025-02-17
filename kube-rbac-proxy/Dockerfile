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
# https://github.com/brancz/kube-rbac-proxy

# Builder stage
FROM golang:1.21-bullseye AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y git make

WORKDIR /src
RUN git clone https://github.com/brancz/kube-rbac-proxy.git && \
    cd kube-rbac-proxy && \
    git checkout 4e78316a56a47e3c05e572a4dba10c4f8a88c994

WORKDIR /src/kube-rbac-proxy

# Build with explicit flags
ENV GOARCH=amd64 \
    GOOS=linux \
    CGO_ENABLED=0 \
    GO111MODULE=on

RUN make build

FROM quay.io/astronomer/ap-base:3.20.5
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

COPY --from=builder /src/kube-rbac-proxy/_output/kube-rbac-proxy-linux-amd64 /usr/local/bin/kube-rbac-proxy

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

RUN adduser -u 65533 -S kube-rbac-proxy -G nogroup

USER 65533:65533

ENTRYPOINT ["/entrypoint.sh"]