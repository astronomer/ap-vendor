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

# https://hub.docker.com/r/grafana/grafana/tags
FROM cgr.dev/astronomer.io/grafana:12.2.2
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root

# Replace passwd/group but keep root user
RUN echo -e "root:x:0:0:root:/root:/bin/sh\ngrafana:x:472:472:grafana:/var/lib/grafana:/sbin/nologin" > /etc/passwd && \
    echo -e "root:x:0:\ngrafana:x:472:" > /etc/group && \
    chown -R 472:472 /var/lib/grafana /etc/grafana

# Install singlestat panel plugin
RUN grafana cli plugins install grafana-singlestat-panel

# Copy default dashboards and datasource configuration
COPY include/*.json /var/lib/grafana/dashboards/
COPY include/dashboard.yaml /etc/grafana/provisioning/dashboards/dashboard.yaml
COPY include/wait-for-db.sh /wait-for-db.sh

USER 472
