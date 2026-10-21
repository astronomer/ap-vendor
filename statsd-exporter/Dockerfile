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

#https://hub.docker.com/r/prom/statsd-exporter/tags
FROM cgr.dev/astronomer.io/ap-statsd-exporter:0.31.0-dev
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

COPY include/mappings.yml /etc/statsd-exporter/mappings.yml
COPY include/mappings-gen2.yml /etc/statsd-exporter/mappings-gen2.yml

# ca-certificates-bundle 20260909-r3 drops the eMudhra-compromised root (PINF-1304); remove once the base image ships it.
COPY --from=cgr.dev/chainguard/static:latest@sha256:17367e4d3ae2b46c3290858e483fac09be085c92b372360fe3bf6a6150848fde \
    /etc/ssl/certs/ca-certificates.crt \
    /etc/ssl/certs/.ca-certificates.crt.sha256 \
    /etc/ssl/certs/

USER 65534
