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
FROM quay.io/astronomer/ap-base:3.20.3-1
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

RUN apk add --no-cache git git-daemon
COPY entrypoint.sh /

# UID and GID must match git-sync, which are both 65533. There is
# already a group 'nogroup' on 65533 so just add git-daemon to that.
RUN adduser -u 65533 -S git-daemon -G nogroup

USER 65533:65533

ENTRYPOINT /entrypoint.sh
