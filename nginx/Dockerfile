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

# https://github.com/kubernetes/ingress-nginx
FROM k8s.gcr.io/ingress-nginx/controller:v1.11.6
LABEL maintainer="Astronomer <humans@astronomer.io>"
USER root
RUN apk upgrade --no-cache
# dont require capability NET_BIND_SERVICE - does prevent using ports below 1024 though
RUN apk add libcap
RUN  setcap cap_net_bind_service=-ep /nginx-ingress-controller
RUN  setcap cap_net_bind_service=-ep /usr/local/nginx/sbin/nginx
RUN  setcap cap_net_bind_service=-ep /usr/bin/dumb-init
USER www-data
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
