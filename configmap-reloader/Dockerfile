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

# https://github.com/jimmidyson/configmap-reload
# https://hub.docker.com/r/jimmidyson/configmap-reload/tags
FROM ghcr.io/jimmidyson/configmap-reload:v0.11.1 as base

# https://hub.docker.com/_/busybox?tab=tags
FROM busybox:1.36.1
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# nobody user
USER 65534

COPY  --from=base /configmap-reload /configmap-reload

ENTRYPOINT ["/configmap-reload"]
