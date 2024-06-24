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

# https://hub.docker.com/r/prom/alertmanager/tags?page=1&ordering=last_updated
FROM prom/alertmanager:v0.27.0 AS UPSTREAM

FROM quay.io/astronomer/ap-base:3.18.6-2
LABEL maintainer="Astronomer <humans@astronomer.io>"
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

RUN mkdir -p /alertmanager /etc/alertmanager && \
    chown -R nobody:nobody /etc/alertmanager /alertmanager

COPY --from=UPSTREAM /bin/amtool /usr/local/bin
COPY --from=UPSTREAM /bin/alertmanager /usr/local/bin
COPY --from=UPSTREAM /etc/alertmanager/alertmanager.yml   /etc/alertmanager/alertmanager.yml

USER       nobody
EXPOSE     9093
VOLUME     [ "/alertmanager" ]
WORKDIR    /alertmanager
ENTRYPOINT [ "/usr/local/bin/alertmanager" ]
CMD        [ "--config.file=/etc/alertmanager/alertmanager.yml", \
             "--storage.path=/alertmanager" ]

USER 65534