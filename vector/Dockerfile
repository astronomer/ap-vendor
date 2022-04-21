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

FROM python:3.10-buster as downloader

ENV VECTOR_VERSION 0.21.0

RUN curl -fsSL https://github.com/vectordotdev/vector/releases/download/v${VECTOR_VERSION}/vector-${VECTOR_VERSION}-x86_64-unknown-linux-gnu.tar.gz \
    | tar --directory=/usr/local/bin/ --strip-components=3 --no-anchored -xzf - vector-x86_64-unknown-linux-gnu/bin/vector

FROM python:3.10-slim

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

COPY --from=downloader /usr/local/bin/vector /usr/local/bin/vector

ADD sidecar_server.py terminate_server.py /usr/local/bin/

USER nobody:nogroup

# Unset upstream entrypoint
ENTRYPOINT []
