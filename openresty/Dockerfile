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


# https://github.com/openresty/docker-openresty/
# https://hub.docker.com/r/openresty/openresty/tags
FROM cgr.dev/astronomer.io/openresty:1.27.1

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

# All temp directories already exist in /var/run/openresty/ can be seen from: https://console.chainguard.dev/org/astronomer.io/images/organization/image/openresty/overview#chainguard-container-for-openresty
# Permissions are already configured correctly
# No RUN commands needed with distroless images

USER 65534
