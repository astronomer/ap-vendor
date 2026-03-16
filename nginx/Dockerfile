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

FROM cgr.dev/astronomer.io/ingress-nginx-controller:1.14.4-dev

RUN apk add --no-cache \
    gcc \
    make \
    git \
    pcre2-dev \
    zlib-dev \
    zlib-static \
    openssl-dev \
    linux-headers \
    wget \
    busybox

RUN git clone --depth=1 https://github.com/yaoweibin/ngx_http_substitutions_filter_module /tmp/subs_module

RUN sed -i 's/return memchr(l, (int)\*cs, l_len);/return (u_char *)memchr(l, (int)*cs, l_len);/' \
    /tmp/subs_module/ngx_http_subs_filter_module.c

WORKDIR /build

RUN set -eux; \
    NGINX_VERSION=$(nginx -v 2>&1 | sed -E 's|.*nginx/([0-9.]+).*|\1|'); \
    echo "Detected nginx version: $NGINX_VERSION"; \
    wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz; \
    tar -xzf nginx-${NGINX_VERSION}.tar.gz; \
    mv nginx-${NGINX_VERSION} nginx-src; \
    cd nginx-src; \
    ./configure --with-compat --add-dynamic-module=/tmp/subs_module; \
    make modules
FROM cgr.dev/astronomer.io/ingress-nginx-controller:1.14.4-dev
LABEL maintainer="Astronomer <humans@astronomer.io>"
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER root

COPY --from=builder /build/nginx-*/objs/ngx_http_subs_filter_module.so \
     /etc/nginx/modules/ngx_http_subs_filter_module.so

RUN chmod 644 /etc/nginx/modules/ngx_http_subs_filter_module.so && \
    apk add libcap && \
    setcap cap_net_bind_service=-ep /usr/bin/nginx-ingress-controller && \
    setcap cap_net_bind_service=-ep /usr/bin/dumb-init

USER www-data
