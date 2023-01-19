FROM loadimpact/k6:0.42.0 AS k6official

FROM node:16.15-alpine3.16

RUN apk upgrade && apk add bash --no-cache && rm -rf /var/cache/apk/*

COPY --from=k6official /usr/bin/k6 /usr/bin/k6

ENTRYPOINT ["/bin/bash"]
