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

FROM bitnami/postgresql:17.4.0-debian-12-r15
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV POSTGRESQL_MAX_CONNECTIONS=200

USER root
RUN apt-get update && apt-get -y upgrade
RUN addgroup postgres --gid 1001 && usermod -u 1001 -g 1001 postgres

RUN chown -R 1001:1001 /opt/bitnami /bitnami/postgresql

USER 1001
