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
FROM grafana/grafana:10.0.9
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# apk updates
USER root
RUN apk upgrade --no-cache
USER root

RUN apk add --no-cache shadow && \
    addgroup --gid 472 grafana && \
    gpasswd -d grafana root && \
    usermod -g grafana grafana && \
    apk del shadow && \
    chown -R grafana:grafana /usr/share/grafana
USER 472

# Install singlestat panel plugin
RUN grafana cli plugins install grafana-singlestat-panel

# Copy default dashboards and datasource configuration
COPY include/*.json /var/lib/grafana/dashboards/
COPY include/dashboard.yaml /etc/grafana/provisioning/dashboards/dashboard.yaml
COPY include/wait-for-db.sh /wait-for-db.sh
