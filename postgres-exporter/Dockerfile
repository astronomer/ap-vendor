#
# Copyright 2020 Astronomer Inc.
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

# https://hub.docker.com/r/prometheuscommunity/postgres-exporter
# https://github.com/prometheus-community/postgres_exporter/blob/v0.10.0/Dockerfile

FROM quay.io/prometheuscommunity/postgres-exporter:v0.14.0 AS upstream

FROM quay.io/astronomer/ap-base:3.18.3

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
LABEL maintainer="Astronomer <humans@astronomer.io>"

COPY --from=upstream  /bin/postgres_exporter /bin/postgres_exporter
COPY include/entrypoint /entrypoint
COPY include/healthcheck /healthcheck

USER 65534
ENTRYPOINT [ "/entrypoint" ]


