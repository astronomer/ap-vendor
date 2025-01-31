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

# First stage: get git-sync binary
FROM registry.k8s.io/git-sync/git-sync:v4.2.3 AS upstream

# Final stage: use ap-base
FROM quay.io/astronomer/ap-base:3.20.3
LABEL maintainer="Astronomer <humans@astronomer.io>"

# Make it possible to override the UID/GID
ARG UID=65533
ARG GID=65533
ARG BUILD_NUMBER=-1
ARG USER=git-sync

LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# Copy git-sync binary from upstream
COPY --from=upstream /git-sync /usr/local/bin/

# Update packages
RUN apk upgrade --no-cache

# Create user and group
RUN addgroup -g $GID -S $USER \
    && adduser -D -S -s /sbin/nologin -G $USER -u $UID $USER

# Set the GITSYNC_ROOT environment variable
ENV GITSYNC_ROOT=/git
ENV HOME=/tmp

# Switch to non-root user
USER $UID

# Configure git safe directory
RUN git config --global --add safe.directory /git

# Set working directory
WORKDIR /tmp

ENTRYPOINT ["/usr/local/bin/git-sync"]
