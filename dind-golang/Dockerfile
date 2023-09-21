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

# https://hub.docker.com/_/docker?tab=tags&page=1&name=dind-alpine
FROM docker:20.10.24-dind-alpine3.18
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

ENV GOLANG_VERSION 1.19.3

#
# Install Golang
#

RUN apk add --no-cache \
                ca-certificates

RUN set -eux; \
        apk add --update --no-cache --virtual .build-deps openssl go ; \
        apk add --update --no-cache make bash gcc g++ libc-dev git curl musl-dev util-linux-dev; \
        export \
                GOROOT_BOOTSTRAP="$(go env GOROOT)" \
                GOOS="linux" \
                GOARCH="amd64" \
                CGO_ENABLED=0 \
        ; \
        \
        wget -O go.tgz "https://golang.org/dl/go$GOLANG_VERSION.src.tar.gz"; \
        echo '18ac263e39210bcf68d85f4370e97fb1734166995a1f63fb38b4f6e07d90d212 *go.tgz' | sha256sum -c -; \
        tar -C /usr/local -xzf go.tgz; \
        rm go.tgz; \
        \
        cd /usr/local/go/src; \
        ./make.bash; \
        \
        rm -rf \
# https://github.com/golang/go/blob/0b30cf534a03618162d3015c8705dd2231e34703/src/cmd/dist/buildtool.go#L121-L125
                /usr/local/go/pkg/bootstrap \
# https://golang.org/cl/82095
# https://github.com/golang/build/blob/e3fe1605c30f6a3fd136b561569933312ede8782/cmd/release/releaselet.go#L56
                /usr/local/go/pkg/obj \
        ; \
        apk del .build-deps; \
        \
        export PATH="/usr/local/go/bin:$PATH"; \
        go version

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

RUN curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin v1.47.3

RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 777 "$GOPATH"
WORKDIR $GOPATH
