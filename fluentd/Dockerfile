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

FROM debian:sid-slim

LABEL maintainer="Astronomer <humans@astronomer.io>"
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ARG BUILD_NUMBER=-1
ARG DEBIAN_FRONTEND=noninteractive

COPY include/Gemfile /Gemfile

# 1. Install & configure dependencies.
# 2. Install fluentd via ruby.
# 3. Remove build dependencies.
# 4. Cleanup leftover caches & files.
RUN set -o xtrace && \
    BUILD_DEPS="build-essential make gcc g++ libc6-dev ruby-dev bundler libffi-dev" \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
                     $BUILD_DEPS \
                     ca-certificates \
                     libjemalloc2 \
                     ruby \
    && echo 'gem: --no-document' >> /etc/gemrc \
    && gem install bundler \
    && gem install --file Gemfile \
    && gem list \
    && apt-get purge -y --auto-remove \
                     -o APT::AutoRemove::RecommendsImportant=false \
                     $BUILD_DEPS \
    && apt-get clean -y \
    && rm -rf \
        /var/cache/debconf/* \
        /var/lib/apt/lists/* \
        /var/log/* \
       /tmp/* \
       /var/tmp/* \
       /usr/lib/ruby/gems/*/cache/*.gem \
       /usr/lib/ruby/gems/2.*/gems/fluentd-*/test \
    && ulimit -n 65536 # Ensure fluent has enough file descriptors

RUN groupadd -r fluent && useradd -r -g fluent fluent \
    # for log storage (maybe shared with host)
    && mkdir -p /fluentd/log \
    # configuration/plugins path (default: copied from .)
    && mkdir -p /fluentd/etc /fluentd/plugins \
    && chown -R fluent /fluentd && chgrp -R fluent /fluentd

# Copy the Fluentd configuration file for logging Docker container logs.
COPY include/fluent.conf /etc/fluent/fluent.conf

# Expose prometheus metrics.
EXPOSE 80

ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2

# Start Fluentd to pick up our config that watches Docker container logs.
RUN mkdir -p /var/log/journal

# The helm chart may call this if istio is enabled
# to prevent a race condition
COPY include/wait-for-istio-proxy.rb /wait-for-istio-proxy.rb

USER fluent

CMD exec /usr/local/bin/fluentd ${FLUENTD_ARGS}
