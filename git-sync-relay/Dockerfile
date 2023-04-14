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

# https://github.com/kubernetes/git-sync/releases

FROM quay.io/astronomer/ap-base:3.16.5
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

RUN apk update && apk upgrade --available && apk add --no-cache git git-daemon openssh-client
COPY gitsync.sh /gitsync.sh
RUN mkdir -p /git

RUN adduser -u 65533 -S git-sync -G nogroup
USER 65533:65533

RUN git config --global --add safe.directory /git
ENTRYPOINT /gitsync.sh
