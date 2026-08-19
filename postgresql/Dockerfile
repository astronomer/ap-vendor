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

# https://hub.docker.com/r/bitnami/postgresql/tags/

FROM cgr.dev/astronomer.io/ap-postgres:17.10
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV POSTGRESQL_MAX_CONNECTIONS=200

# PINF-347: the base image's own /usr/bin/docker-entrypoint.sh only writes
# postgresql.conf/pg_hba.conf on first init, and silently skips that step on
# every upgrade (where it finds an already-initialized data directory, i.e.
# PG_VERSION already present). That leaves upgraded installs with a valid
# data directory but no server config file, and postgres refuses to start.
# docker-entrypoint-wrapper.sh repairs only that exact case - using the
# config this same image would have produced on a fresh install - before
# handing off to the real entrypoint. Fresh installs and already-healthy
# instances are untouched. See the wrapper script for the full explanation.
COPY postgresql.conf pg_hba.conf /opt/astronomer/conf/
COPY docker-entrypoint-wrapper.sh /usr/local/bin/docker-entrypoint-wrapper.sh
RUN chmod 0755 /usr/local/bin/docker-entrypoint-wrapper.sh

USER 1001

ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["postgres"]
