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

FROM quay.io/astronomer/ap-base:3.18.8

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV NATS_SERVER 2.10.18

ENV NATS_SERVER_SHA256_CHECKSUM 7760fe7347ba8e8daf4474811cf7fc301713aa8f3d4e0787d3e79a496dd537b2

RUN addgroup -g 1000 -S nats \
	&& adduser -u 1000 -S nats -G nats

RUN set -eux ; \
	url="https://github.com/nats-io/nats-server/releases/download/v${NATS_SERVER}/nats-server-v${NATS_SERVER}-linux-amd64.tar.gz" ; \
	sha256=${NATS_SERVER_SHA256_CHECKSUM} ; \
	wget -O nats-server.tar.gz "${url}" ; \
	echo "${sha256} *nats-server.tar.gz" | sha256sum -c - ; \
	apk add --no-cache ca-certificates ; \
	apk add --no-cache --virtual buildtmp ; \
	tar -xf nats-server.tar.gz ; \
	rm nats-server.tar.gz ; \
	mv "nats-server-v${NATS_SERVER}-linux-amd64/nats-server" /usr/local/bin ; \
	rm -rf "nats-server-v${NATS_SERVER}-linux-amd64" ; \
	apk del --no-cache --no-network buildtmp

COPY --chown=1000:1000 nats-server.conf /etc/nats/nats-server.conf
COPY --chown=1000:1000 docker-entrypoint.sh /usr/local/bin
USER 1000
EXPOSE 4222 8222 6222
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["nats-server", "--config", "/etc/nats/nats-server.conf"]
