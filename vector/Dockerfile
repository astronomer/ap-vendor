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

FROM cgr.dev/astronomer.io/ap-vector:0.48.0-dev
LABEL maintainer="Astronomer <humans@astronomer.io>"

USER root

RUN mkdir -p /opt && \
    wget https://github.com/indygreg/python-build-standalone/releases/download/20250101/cpython-3.12.12-x86_64-unknown-linux-gnu-install_only.tar.gz && \
    tar -xzf cpython-3.12.12-x86_64-unknown-linux-gnu-install_only.tar.gz -C /opt && \
    rm cpython-3.12.12-x86_64-unknown-linux-gnu-install_only.tar.gz

COPY --chmod=755 sidecar_server.py /usr/local/bin/
COPY vector.toml /etc/vector/vector.toml

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENTRYPOINT ["/usr/bin/python3", "/usr/local/bin/sidecar_server.py"]
