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
# Stage 1: Get upgraded packages and bash
FROM debian:bookworm-slim as base
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y bash && \
    rm -rf /var/lib/apt/lists/*

# Final stage
FROM registry.k8s.io/git-sync/git-sync:v4.2.3
LABEL maintainer="Astronomer <humans@astronomer.io>"
USER root

# Copy upgraded bash and necessary libraries
COPY --from=base /bin/bash /bin/bash
COPY --from=base /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/
COPY --from=base /lib/x86_64-linux-gnu/libtinfo.so.6 /lib/x86_64-linux-gnu/

# Return to the non-root user
USER 65533:65533
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
RUN git config --global --add safe.directory /git
