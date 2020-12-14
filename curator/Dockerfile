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

FROM astronomerinc/ap-base:3.12.2

RUN apk --no-cache add \
      python3 py-setuptools py-pip gcc libffi py-cffi python3-dev \
      libffi-dev py-openssl musl-dev linux-headers openssl-dev libssl1.1 && \
    apk --no-cache add -u --repository=http://dl-cdn.alpinelinux.org/alpine/edge/main \
      sqlite-libs && \
    pip install -U setuptools wheel && \
    pip install elasticsearch-curator==5.8.1 && \
    pip install boto3==1.12.42 && \
    pip install requests-aws4auth==0.9 && \
    pip install cryptography==2.6.1 && \
	pip install pyOpenSSL && \
    apk del py-pip gcc python3-dev libffi-dev musl-dev linux-headers openssl-dev && \
    sed -i '/import sys/a urllib3.contrib.pyopenssl.inject_into_urllib3()' /usr/bin/curator && \
    sed -i '/import sys/a import urllib3.contrib.pyopenssl' /usr/bin/curator && \
    sed -i '/import sys/a import urllib3' /usr/bin/curator

USER nobody:nobody

ENTRYPOINT ["/usr/bin/curator"]

LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
