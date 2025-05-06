FROM mcr.microsoft.com/playwright:v1.53.0-noble
LABEL maintainer="Astronomer <humans@astronomer.io>"

ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER

WORKDIR /usr/app
RUN npm install playwright
COPY server.ts /usr/app/
ENTRYPOINT [ "node", "./server.ts" ]