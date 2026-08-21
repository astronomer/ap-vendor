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

# We have an open request with chainguard for them to begin building this image: https://console.chainguard.dev/org/astronomer.io/requests/pending#
# Using the standard (non-rootless) image rather than the rootless variant:
# downstream test suites `docker exec` into this container as root to do
# configuration work, and the rootless image has no root user to exec as.
# The standard image's entrypoint still starts as root and internally drops
# the forgejo/git process to USER_UID/USER_GID (default 1000:1000) at
# runtime, so we leave USER unset here rather than forcing it.
FROM codeberg.org/forgejo/forgejo:16.0.2
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
