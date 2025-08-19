# Minimal base image - duck typed for any Linux
ARG BASE_IMAGE=alpine:3.19

FROM ${BASE_IMAGE}

# Create user and home directory - works on all distros
RUN echo 'astro:x:50000:50000::/home/astro:/sbin/nologin' >> /etc/passwd && \
    echo 'astro:x:50000:' >> /etc/group && \
    mkdir -p /home/astro && \
    chown 50000:50000 /home/astro

USER 50000
WORKDIR /home/astro
