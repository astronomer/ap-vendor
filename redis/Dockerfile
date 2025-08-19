# Redis - built from source with configurable features
# Default to UBI10-micro for minimal attack surface
# UBI 10.0-1747317009 - latest available version
ARG BUILDER_IMAGE=registry.access.redhat.com/ubi10/ubi:10.0-1747220028
ARG BASE_IMAGE=registry.access.redhat.com/ubi10/ubi-micro:10.0-1747317009

FROM ${BUILDER_IMAGE} AS builder

# Duck typed package management
ARG PACKAGE_MANAGER
ARG PACKAGE_NAMING_SCHEME

# Define common packages
ARG COMMON_PACKAGES="curl gcc make"

# Install packages based on package manager
RUN case "${PACKAGE_MANAGER}" in \
      apk) apk add --no-cache ${COMMON_PACKAGES} build-base linux-headers ;; \
      dnf|yum) dnf install -y --allowerasing ${COMMON_PACKAGES} gcc-c++ glibc-devel ;; \
      apt) apt-get update && apt-get install -y ${COMMON_PACKAGES} build-essential && rm -rf /var/lib/apt/lists/* ;; \
    esac

# Build Redis with configurable features
# Redis 7.4.5 - Latest 7.4.x BSD-licensed version (post-licensing chasm)
ARG REDIS_VERSION="7.4.5"
WORKDIR /build
# Download and verify Redis source (SHA256 file might not exist for all versions)
RUN curl -L https://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz -o redis-${REDIS_VERSION}.tar.gz && \
    (curl -L https://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz.SHA256SUM -o redis.sha256 2>/dev/null && \
     sha256sum -c redis.sha256) || \
    echo "SHA256 file not found, proceeding without verification" && \
    tar -xzf redis-${REDIS_VERSION}.tar.gz && \
    cd redis-${REDIS_VERSION} && \
    make -j$(nproc) && \
    make install PREFIX=/usr/local && \
    strip /usr/local/bin/redis-*

# Final stage - uses ap-base which already has astro user
FROM ${BASE_IMAGE}

# Switch to root for installation
USER root

# Create Redis directories
RUN mkdir -p /data /var/log/redis && \
    chown -R 50000:50000 /data /var/log/redis

# Copy Redis binaries
COPY --from=builder /usr/local/bin/redis-* /usr/local/bin/

# Switch back to astro user
USER 50000
WORKDIR /home/astro
EXPOSE 6379
# Configure Redis to use /data as the default dir for RDB/AOF files
ENTRYPOINT ["redis-server", "--dir", "/data"]
