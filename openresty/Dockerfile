#
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


# https://github.com/openresty/docker-openresty/
# https://hub.docker.com/r/openresty/openresty/tags
FROM docker.io/openresty/openresty:1.21.4.2-0-alpine
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

RUN mkdir -p /usr/local/openresty/nginx/client_body_temp \
    && mkdir -p /usr/local/openresty/nginx/proxy_temp \
    && mkdir -p /usr/local/openresty/nginx/client_temp \
    && mkdir -p /usr/local/openresty/nginx/fastcgi_temp \
    && mkdir -p /usr/local/openresty/nginx/uwsgi_temp \
    && mkdir -p /usr/local/openresty/nginx/scgi_temp \
    && chown -R nobody:nobody /var/run/openresty \
    && chown -R nobody:nobody /usr/local/openresty \
    && chmod -R g+w /usr/local/openresty

# upgrade apk packages
RUN apk upgrade --no-cache

USER 65534
