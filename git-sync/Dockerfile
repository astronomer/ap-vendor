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

# https://github.com/kubernetes/git-sync/releases
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
# https://github.com/kubernetes/git-sync/releases

FROM golang:1.26.4-alpine3.22 AS builder
RUN apk add --no-cache git
RUN git clone https://github.com/kubernetes/git-sync.git /tmp/git-sync && \
    cd /tmp/git-sync && \
    git checkout v4.4.1 && \
    CGO_ENABLED=0 go build -o /usr/local/bin/git-sync . && \
    cd / && rm -rf /tmp/git-sync

FROM quay.io/astronomer/ap-base:2026.6.4
LABEL maintainer="Astronomer <humans@astronomer.io>"
USER root
RUN apk update && apk upgrade --available && \
    apk add --no-cache openssh-client git
COPY --from=builder /usr/local/bin/git-sync /usr/local/bin/git-sync
RUN echo "git-sync:x:65533:65533::/tmp:/sbin/nologin" >> /etc/passwd
RUN mkdir -m 02775 /git && chown 65533:65533 /git
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
RUN git config --global --add safe.directory /git
USER 65533
ENTRYPOINT  [ "git-sync" ]
