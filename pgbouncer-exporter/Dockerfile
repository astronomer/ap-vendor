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

# https://hub.docker.com/r/jbub/pgbouncer_exporter
FROM jbub/pgbouncer_exporter:v0.13.0 AS builder

FROM quay.io/astronomer/ap-base:3.15.2

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

COPY --from=builder /bin/pgbouncer_exporter /bin

RUN addgroup -S pgexporter \
    && adduser -D -S -s /sbin/nologin -G pgexporter pgexporter

USER pgexporter

HEALTHCHECK CMD ["pgbouncer_exporter", "health"]

ENTRYPOINT ["pgbouncer_exporter"]
CMD ["server"]
