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
# Until that merges we are using the rootless variant: the standard image's
# s6-overlay entrypoint needs root to chown /data and generate host SSH keys
# before it drops privileges to USER_UID/USER_GID, so forcing USER on that
# image breaks first-run setup. The rootless image bakes in a Go SSH server
# instead of OpenSSH/s6 and is built to run entirely as a non-root, arbitrary
# UID/GID.
FROM codeberg.org/forgejo/forgejo:16.0.2-rootless
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
USER 1000:1000
