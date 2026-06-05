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

# https://hub.docker.com/r/datadog/dogstatsd/tags
FROM datadog/dogstatsd:7.79.2
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root

# The upstream image runs as root. Create an unprivileged "datadog" user and
# hand it ownership of every path dogstatsd reads from or writes to at runtime:
#   - /dogstatsd             : the entrypoint runs `chmod +x` on it, which only
#                              succeeds if the running user owns the file
#   - /etc/datadog-agent     : config dir; auth_token + ipc_cert.pem are written
#                              here on startup for IPC auth
#   - /var/log/datadog       : dogstatsd.log
#   - /opt/datadog-agent/run : run_path persistent state
RUN addgroup -g 1000 -S datadog \
    && adduser -u 1000 -S datadog -G datadog \
    && chmod +x /dogstatsd \
    && mkdir -p /var/log/datadog /opt/datadog-agent/run \
    && chown -R datadog:datadog /dogstatsd /etc/datadog-agent /var/log/datadog /opt/datadog-agent

COPY --chown=datadog:datadog include/dogstatsd.yaml /etc/datadog-agent/dogstatsd.yaml

USER datadog
