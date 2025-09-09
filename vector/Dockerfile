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

# https://hub.docker.com/r/curlimages/curl/tags
# https://github.com/vectordotdev/vector/releases/

FROM cgr.dev/chainguard/python:latest as python-stage

FROM cgr.dev/astronomer.io/ap-vector:latest-dev
LABEL maintainer="Astronomer <humans@astronomer.io>"

COPY --from=python-stage /usr/lib/python3* /usr/lib/
COPY --from=python-stage /usr/lib/libpython* /usr/lib/
COPY --from=python-stage /lib/ /lib/

COPY --from=python-stage /usr/bin/python3 /usr/bin/python3

COPY --chmod=755 sidecar_server.py /usr/local/bin/
COPY vector.toml /etc/vector/vector.toml

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENTRYPOINT ["/usr/bin/python3", "/usr/local/bin/sidecar_server.py"]
