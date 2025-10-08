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

# https://quay.io/repository/astronomer/ap-base?tab=tags
# Stage 1: Patched SQLite library
FROM cgr.dev/chainguard/wolfi-base:latest AS sqlite-builder
RUN apk update && apk add sqlite-libs --no-cache

# Stage 2: Final image
FROM quay.io/astronomer/ap-base:3.21.3-6
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

COPY --from=sqlite-builder /usr/lib/libsqlite3.so* /usr/lib/

USER root

RUN if [ ! -f /usr/bin/python3 ]; then \
      ln -s /usr/bin/python /usr/bin/python3 2>/dev/null || true; \
    fi

USER 65534

ENTRYPOINT ["/usr/bin/curator"]
