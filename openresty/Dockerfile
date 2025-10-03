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
# Build stage using -dev variant
FROM cgr.dev/astronomer.io/openresty:1.27.1-dev AS builder

# Create temp directories under /tmp (which is mounted as writable in K8s)
RUN mkdir -p /tmp/nginx/client_body_temp \
    && mkdir -p /tmp/nginx/proxy_temp \
    && mkdir -p /tmp/nginx/fastcgi_temp \
    && mkdir -p /tmp/nginx/uwsgi_temp \
    && mkdir -p /tmp/nginx/scgi_temp \
    && chown -R 65534:65534 /tmp/nginx

# Create nginx config snippet to use /tmp paths
RUN printf 'client_body_temp_path /tmp/nginx/client_body_temp;\n\
proxy_temp_path /tmp/nginx/proxy_temp;\n\
fastcgi_temp_path /tmp/nginx/fastcgi_temp;\n\
uwsgi_temp_path /tmp/nginx/uwsgi_temp;\n\
scgi_temp_path /tmp/nginx/scgi_temp;\n' > /etc/nginx/conf.d/temp_paths.conf

# Upgrade packages
RUN apk upgrade --no-cache

# Final stage using distroless runtime
FROM cgr.dev/astronomer.io/openresty:1.27.1

# Copy the nginx config that sets temp paths to /tmp
COPY --from=builder /etc/nginx/conf.d/temp_paths.conf /etc/nginx/conf.d/temp_paths.conf

# Note: /tmp directories will be created by the emptyDir volume mount in K8s
# We don't need to copy them because the volume mount happens at runtime

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

USER 65534
