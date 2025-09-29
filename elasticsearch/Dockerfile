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
FROM cgr.dev/astronomer.io/ap-elasticsearch:8.18.6
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER 0

RUN apk add --no-cache curl

# Downloaded the lucene-backward-codecs JAR matching ES 8.18.6
# Using the version of Lucene bundled in 8.18.6 (checked with `bin/elasticsearch --version`)
RUN curl -L -o /usr/share/elasticsearch/lib/lucene-backward-codecs-9.12.0.jar \
    https://repo1.maven.org/maven2/org/apache/lucene/lucene-backward-codecs/9.12.0/lucene-backward-codecs-9.12.0.jar && \
    chown elasticsearch:elasticsearch /usr/share/elasticsearch/lib/lucene-backward-codecs-9.12.0.jar

RUN deluser elasticsearch 2>/dev/null || true && \
    delgroup elasticsearch 2>/dev/null || true && \
    addgroup -g 1000 elasticsearch && \
    adduser -D -u 1000 -G elasticsearch -s /bin/sh elasticsearch

USER elasticsearch
