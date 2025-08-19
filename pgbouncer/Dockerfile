# PgBouncer - built from source with configurable features
# Default to Alpine 3.19 (released 2023-12-07, LTS until 2025-11-01)
ARG BUILDER_IMAGE=alpine:3.19
ARG BASE_IMAGE=alpine:3.19

FROM ${BUILDER_IMAGE} AS builder

# Duck typed package management
ARG PACKAGE_MANAGER
ARG PACKAGE_NAMING_SCHEME

# Define common packages
ARG COMMON_PACKAGES="git autoconf automake libtool"

# Install packages based on package manager
RUN case "${PACKAGE_MANAGER}" in \
      apk) apk add --no-cache ${COMMON_PACKAGES} build-base libevent-dev openssl-dev c-ares-dev ;; \
      dnf|yum) dnf install -y --allowerasing ${COMMON_PACKAGES} gcc make libevent-devel openssl-devel pkgconfig ;; \
      apt) apt-get update && apt-get install -y ${COMMON_PACKAGES} build-essential libevent-dev libssl-dev libc-ares-dev && rm -rf /var/lib/apt/lists/* ;; \
    esac

# Build PgBouncer with configurable features
# PgBouncer 1.21.0 released 2023-10-16
ARG PGBOUNCER_VERSION="1_21_0"
# Build with OpenSSL for TLS support, use libevent for DNS
ARG PGBOUNCER_FEATURES="--with-openssl"
WORKDIR /build
RUN git clone https://github.com/pgbouncer/pgbouncer.git && \
    cd pgbouncer && \
    git checkout pgbouncer_${PGBOUNCER_VERSION} && \
    git submodule update --init && \
    ./autogen.sh && \
    ./configure ${PGBOUNCER_FEATURES} && \
    make -j$(nproc) pgbouncer && \
    strip pgbouncer

# Final stage - uses ap-base which already has astro user
FROM ${BASE_IMAGE}

# Switch to root for installation
USER root

# Copy runtime libraries from builder
# Alpine uses /usr/lib, UBI uses /usr/lib64
# We need to determine which directory exists and copy from there
RUN --mount=from=builder,source=/usr,target=/builder_usr \
    if [ -d /builder_usr/lib64 ]; then \
        mkdir -p /usr/lib64 && \
        cp -a /builder_usr/lib64/libevent*.so* /usr/lib64/ 2>/dev/null || true && \
        cp -a /builder_usr/lib64/libssl*.so* /usr/lib64/ 2>/dev/null || true && \
        cp -a /builder_usr/lib64/libcrypto*.so* /usr/lib64/ 2>/dev/null || true && \
        cp -a /builder_usr/lib64/libcares* /usr/lib64/ 2>/dev/null || true && \
        cp -a /builder_usr/lib64/libz*.so* /usr/lib64/ 2>/dev/null || true; \
    else \
        mkdir -p /usr/lib && \
        cp -a /builder_usr/lib/libevent*.so* /usr/lib/ 2>/dev/null || true && \
        cp -a /builder_usr/lib/libssl*.so* /usr/lib/ 2>/dev/null || true && \
        cp -a /builder_usr/lib/libcrypto*.so* /usr/lib/ 2>/dev/null || true && \
        cp -a /builder_usr/lib/libcares* /usr/lib/ 2>/dev/null || true && \
        cp -a /builder_usr/lib/libz*.so* /usr/lib/ 2>/dev/null || true; \
    fi

# Create required directories
# Note: /var/run might be read-only, so we use /tmp for runtime files
RUN mkdir -p /etc/pgbouncer /tmp/pgbouncer && \
    echo '[databases]' > /etc/pgbouncer/pgbouncer.ini && \
    echo '* = host=localhost' >> /etc/pgbouncer/pgbouncer.ini && \
    echo '[pgbouncer]' >> /etc/pgbouncer/pgbouncer.ini && \
    echo 'listen_addr = 0.0.0.0' >> /etc/pgbouncer/pgbouncer.ini && \
    echo 'auth_type = trust' >> /etc/pgbouncer/pgbouncer.ini && \
    echo 'pidfile = /tmp/pgbouncer/pgbouncer.pid' >> /etc/pgbouncer/pgbouncer.ini && \
    echo 'unix_socket_dir = /tmp/pgbouncer' >> /etc/pgbouncer/pgbouncer.ini && \
    echo 'logfile = ' >> /etc/pgbouncer/pgbouncer.ini && \
    chown -R 50000:50000 /etc/pgbouncer /tmp/pgbouncer

COPY --from=builder /build/pgbouncer/pgbouncer /usr/local/bin/pgbouncer
RUN chmod 755 /usr/local/bin/pgbouncer

# Set library path for Alpine
ENV LD_LIBRARY_PATH=/usr/lib:/lib

# Switch back to astro user
USER 50000
WORKDIR /home/astro
EXPOSE 6432
ENTRYPOINT ["/usr/local/bin/pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]
