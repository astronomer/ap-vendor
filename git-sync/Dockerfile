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
FROM registry.k8s.io/git-sync/git-sync:v4.4.1 AS upstream

FROM quay.io/astronomer/ap-base:3.21.3-5
LABEL maintainer="Astronomer <humans@astronomer.io>"
COPY --from=upstream /git-sync /usr/local/bin/
USER root
RUN apk update && apk upgrade --available && apk add --no-cache git openssh-client
RUN echo "git-sync:x:65533:65533::/tmp:/sbin/nologin" >> /etc/passwd
RUN mkdir -m 02775 /git && chown 65533:65533 /git
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
RUN git config --global --add safe.directory /git
USER 65533
ENTRYPOINT  [ "git-sync" ]
