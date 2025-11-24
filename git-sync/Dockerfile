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
FROM quay.io/astronomer/ap-base:2025.11.3
LABEL maintainer="Astronomer <humans@astronomer.io>"

USER root

# Install git and openssh-client (Go 1.25.1 is already installed)
RUN apk update && apk upgrade --available && \
    apk add --no-cache openssh-client git

# Build git-sync from source with Go 1.25.1
RUN git clone https://github.com/kubernetes/git-sync.git /tmp/git-sync && \
    cd /tmp/git-sync && \
    git checkout v4.4.1 && \
    CGO_ENABLED=0 go build -o /usr/local/bin/git-sync . && \
    cd / && rm -rf /tmp/git-sync

RUN echo "git-sync:x:65533:65533::/tmp:/sbin/nologin" >> /etc/passwd
RUN mkdir -m 02775 /git && chown 65533:65533 /git

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

RUN git config --global --add safe.directory /git

USER 65533
ENTRYPOINT  [ "git-sync" ]
