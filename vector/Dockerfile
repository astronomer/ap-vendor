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
# https://github.com/vectordotdev/vector/releases/

FROM cgr.dev/astronomer.io/ap-vector:latest
LABEL maintainer="Astronomer <humans@astronomer.io>"

# Make it possible to override the UID/GID/username
ARG UID=65534
ARG GID=65534
ARG USER=vector

USER root
RUN apk update && \
    apk add shadow python3 vector && \
    adduser -D -u $UID -g $GID $USER && \
    chown -R $USER:$USER /etc/vector && \
    rm -rf /var/cache/apk/*

COPY sidecar_server.py /usr/local/bin/
COPY vector.toml /etc/vector/vector.toml
RUN chown $USER:$USER /usr/local/bin/sidecar_server.py

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER $USER
ENTRYPOINT ["/usr/local/bin/sidecar_server.py"]
