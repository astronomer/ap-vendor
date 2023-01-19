FROM loadimpact/k6:0.42.0 AS k6official

FROM node:16.15-alpine3.15

RUN apk add bash

COPY --from=k6official /usr/bin/k6 /usr/bin/k6

ENTRYPOINT ["/bin/bash"]
