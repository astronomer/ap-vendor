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
# docker-entrypoint-wrapper.sh repairs only that exact case before handing off
# to the real entrypoint, by running this image's own `initdb` against a
# throwaway scratch directory and lifting the two generated config files out
# of it - not a static copy we maintain ourselves. See the wrapper script for
# the full explanation. Fresh installs and already-healthy instances are
# untouched either way.
#
# postgresql.conf/pg_hba.conf below are NOT used (the wrapper no longer reads
# them - superseded by the initdb-based approach) - kept for reference/
# rollback only. Not copied into the image. Remove once we're confident in
# the new approach.
# COPY postgresql.conf pg_hba.conf /opt/astronomer/conf/
COPY docker-entrypoint-wrapper.sh /usr/local/bin/docker-entrypoint-wrapper.sh
RUN chmod 0755 /usr/local/bin/docker-entrypoint-wrapper.sh

USER 1001

ENTRYPOINT ["/usr/local/bin/docker-entrypoint-wrapper.sh"]
CMD ["postgres"]
