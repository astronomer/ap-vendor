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

FROM ruby:2.7-slim-buster as builder

ARG DEBIAN_FRONTEND=noninteractive

COPY include/Gemfile /Gemfile

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends g++ gcc make && \
    echo 'gem: --no-document' >> /etc/gemrc && \
    gem install --file Gemfile

FROM ruby:2.7-slim-buster

ARG DEBIAN_FRONTEND=noninteractive

# Copy the Fluentd configuration file for logging Docker container logs.
COPY include/fluent.conf /etc/fluent/fluent.conf
COPY --from=builder /usr/local/bundle/ /usr/local/bundle

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends libjemalloc2 && \
    apt-get clean -y && \
    ulimit -n 65536 && \
    rm -rf \
        /var/cache/debconf/* \
        /var/lib/apt/lists/* \
        /var/log/* \
        /var/tmp/* \
        rm -rf /tmp/*

# Expose prometheus metrics.
EXPOSE 80

ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2

# Start Fluentd to pick up our config that watches Docker container logs.
RUN mkdir -p /var/log/journal

# The helm chart may call this if istio is enabled
# to prevent a race condition
COPY include/wait-for-istio-proxy.rb /wait-for-istio-proxy.rb

CMD exec /usr/local/bundle/bin/fluentd ${FLUENTD_ARGS}

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
