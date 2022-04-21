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
ARG GO_VERSION=1.17
FROM golang:${GO_VERSION}-alpine AS builder

ENV AWSESPROXY_DIR /go/src/github.com/abutaha/aws-es-proxy

RUN set -ex \
    && apk add --no-cache make git file

WORKDIR $AWSESPROXY_DIR

# This commit upgrades go version and related PR can be found here: https://github.com/abutaha/aws-es-proxy/pull/109
# waiting for the upstream to merge those changes until then we will checkout to custom commit id
RUN git clone https://github.com/astronomer/aws-es-proxy.git $AWSESPROXY_DIR && git checkout 4b359c78b9052c4cb8145cb92c7d560b99512043

RUN CGO_ENABLED=0 GOOS=linux go build -o aws-es-proxy

FROM quay.io/astronomer/ap-base:3.15.4
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

RUN apk --no-cache add ca-certificates
WORKDIR /home/
COPY --from=builder /go/src/github.com/abutaha/aws-es-proxy/aws-es-proxy /usr/local/bin/

ENV PORT_NUM 9200
EXPOSE ${PORT_NUM}

USER nobody

ENTRYPOINT ["aws-es-proxy"]
CMD ["-h"]
