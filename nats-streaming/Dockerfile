#
# Copyright 2016 Astronomer Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License") ;
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

FROM quay.io/astronomer/ap-base:3.18.7-1

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV NATS_STREAMING_SERVER 0.25.6

ENV NATS_STREAMING_SHA256_CHECKSUM f6fcd66c1150ad17d0571490880225afed0ddc8851f64e2c2b138fc8475aced3

# Create nats-streamming user and group
RUN addgroup -g 1000 -S nats-streaming \
	&& adduser -u 1000 -S nats-streaming -G nats-streaming

RUN set -eux ; \
	url="https://github.com/nats-io/nats-streaming-server/releases/download/v${NATS_STREAMING_SERVER}/nats-streaming-server-v${NATS_STREAMING_SERVER}-linux-amd64.zip" ; \
	sha256=${NATS_STREAMING_SHA256_CHECKSUM} ; \
	wget -O nats-streaming-server.zip "${url}" ; \
	echo "${sha256} *nats-streaming-server.zip" | sha256sum -c - ; \
	apk add --no-cache ca-certificates ; \
	apk add --no-cache --virtual buildtmp unzip ; \
	apk upgrade --no-cache ; \
	unzip nats-streaming-server.zip "nats-streaming-server-v${NATS_STREAMING_SERVER}-linux-amd64/nats-streaming-server" ; \
	rm nats-streaming-server.zip ; \
	mv "nats-streaming-server-v${NATS_STREAMING_SERVER}-linux-amd64/nats-streaming-server" /usr/local/bin ; \
	rmdir "nats-streaming-server-v${NATS_STREAMING_SERVER}-linux-amd64" ; \
	apk del --no-cache --no-network buildtmp

COPY --chown=1000:1000 docker-entrypoint.sh /usr/local/bin
EXPOSE 4222 8222
USER 1000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["nats-streaming-server", "-m", "8222"]
