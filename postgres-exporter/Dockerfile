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

# https://hub.docker.com/r/wrouesnel/postgres_exporter
# https://github.com/wrouesnel/postgres_exporter/blob/v0.8.0/Dockerfile
FROM wrouesnel/postgres_exporter:v0.8.0 AS upstream
# The above 'upstream' layer is FROM scratch (they use a multi-stage build)
# I would like some normal tooling like package manager and shell available.
# In the next update, I think they are migrating from the scratch image,
# so it will likely be unnecessary to perform this multi-stage build.
# https://quay.io/repository/astronomer/ap-base
FROM quay.io/astronomer/ap-base:3.12.3

LABEL maintainer="Astronomer <humans@astronomer.io>"
LABEL io.astronomer.docker=true

# get the user set up with the right UID
COPY --from=upstream /etc/passwd /etc/passwd
# copy the app binary over
COPY --from=upstream /postgres_exporter /postgres_exporter
# this user was copied via /etc/passwd
# UID is 20001
USER postgres_exporter

EXPOSE 9187

COPY include/entrypoint /entrypoint
COPY include/healthcheck /healthcheck

ENTRYPOINT [ "/entrypoint" ]
