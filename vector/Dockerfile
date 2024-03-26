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

# https://hub.docker.com/r/curlimages/curl/tags
FROM curlimages/curl:latest as downloader

# https://github.com/vectordotdev/vector/releases/
ENV VECTOR_VERSION 0.34.0

RUN curl -fsSL https://github.com/vectordotdev/vector/releases/download/v${VECTOR_VERSION}/vector-${VECTOR_VERSION}-x86_64-unknown-linux-musl.tar.gz \
    | tar --directory=/tmp --strip-components=3 -xzf - ./vector-x86_64-unknown-linux-musl/bin/vector

FROM quay.io/astronomer/ap-base:3.18.6

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# Update packages to solve security vulnerabilities
RUN apk add python3

COPY --from=downloader /tmp/vector /usr/local/bin/vector

ADD sidecar_server.py /usr/local/bin/

COPY vector.toml /etc/vector/vector.toml

USER 65534

ENTRYPOINT ["/usr/local/bin/sidecar_server.py"]
