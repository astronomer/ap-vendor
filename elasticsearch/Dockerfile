#
# Copyright 2019 Astronomer Inc.
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

# https://www.docker.elastic.co/r/elasticsearch
FROM docker.elastic.co/elasticsearch/elasticsearch:8.18.2-amd64
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER 0
RUN apt-get update && \
    apt-get install libssl1.1 openssl -y && \
    rm -rf /var/lib/apt/lists/*
RUN gpasswd -d elasticsearch root
USER 1000

USER elasticsearch
