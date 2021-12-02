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

# https://quay.io/repository/astronomer/ap-base?tab=tags
FROM quay.io/astronomer/ap-base:3.15.0
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

RUN set -x ; apk --no-cache add \
      libffi \
      libssl1.1 \
      py3-cffi \
      py3-pip \
      py3-setuptools \
      python3 \
      python3-dev && \
    apk --no-cache add -u --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main \
      py3-cryptography \
      py3-openssl \
      py3-requests \
      py3-urllib3 \
      sqlite-libs && \
    pip install --upgrade --no-cache-dir \
      setuptools \
      wheel \
      elasticsearch \
      elasticsearch-curator \
      boto3 \
      requests-aws4auth && \
    apk del \
      py-pip \
      python3-dev

USER nobody:nobody

ENTRYPOINT ["/usr/bin/curator"]

