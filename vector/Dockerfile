# Vector - Build from source on UBI10
ARG BUILDER_IMAGE=registry.access.redhat.com/ubi10/ubi:latest
ARG BASE_IMAGE=localhost:7787/ap-base:minimal-ubi

FROM ${BUILDER_IMAGE} AS builder

# Install build dependencies for UBI10
RUN dnf install -y \
      curl \
      ca-certificates \
      gcc \
      gcc-c++ \
      make \
      openssl-devel \
      pkg-config \
      perl-core \
      git \
      cmake \
      python3 \
      unzip \
    && dnf clean all

# Install protoc manually since it's not in UBI10 repos
RUN curl -L https://github.com/protocolbuffers/protobuf/releases/download/v24.4/protoc-24.4-linux-x86_64.zip -o protoc.zip && \
    unzip protoc.zip -d /usr/local && \
    rm protoc.zip

# Install Rust with specific version for reproducibility
ARG RUST_VERSION="1.75.0"
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain ${RUST_VERSION}
ENV PATH="/root/.cargo/bin:${PATH}"

# Set up Rust build optimizations for faster compilation
ENV CARGO_BUILD_JOBS=4 \
    CARGO_INCREMENTAL=0 \
    CARGO_NET_RETRY=10 \
    CARGO_NET_TIMEOUT=30

# Build Vector from source
ARG VECTOR_VERSION="0.35.0"
# Include all features needed for the sidecar config
ARG VECTOR_FEATURES="sources-file,sinks-console,sinks-elasticsearch,transforms-filter,transforms-remap,api,api-client"

# Download vector source
WORKDIR /build
RUN curl -L https://github.com/vectordotdev/vector/archive/refs/tags/v${VECTOR_VERSION}.tar.gz | tar xz

# Build with standard target for UBI
WORKDIR /build/vector-${VECTOR_VERSION}

# Create git repo to satisfy build requirements
RUN git init && \
    git config user.email "build@localhost" && \
    git config user.name "Build" && \
    git add . && \
    git commit -m "Build v${VECTOR_VERSION}"

# Build with optimizations for faster compilation
RUN cargo build \
    --release \
    --no-default-features \
    --features "${VECTOR_FEATURES}" \
    -j 4 && \
    strip target/release/vector

# Copy required libraries
RUN mkdir -p /deps && \
    ldd target/release/vector | grep "=> /" | awk '{print $3}' | while read lib; do \
        cp --parents "$lib" /deps/ 2>/dev/null || true; \
    done && \
    # Also copy NSS libraries for hostname resolution
    cp --parents /lib64/libnss_files.so.2 /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libnss_dns.so.2 /deps/ 2>/dev/null || true && \
    # Copy OpenSSL libraries
    cp --parents /lib64/libssl.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libcrypto.so* /deps/ 2>/dev/null || true && \
    # Copy other essential libraries
    cp --parents /lib64/libz.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libgcc_s.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libstdc++.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libm.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libdl.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libpthread.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/libc.so* /deps/ 2>/dev/null || true && \
    cp --parents /lib64/ld-linux-x86-64.so* /deps/ 2>/dev/null || true

# Final stage - minimal base
FROM ${BASE_IMAGE}

# Switch to root for installation
USER root

# Copy the compiled binary and its dependencies
COPY --from=builder --chmod=755 /build/vector-*/target/release/vector /usr/local/bin/vector
COPY --from=builder /deps/ /

# Set library path
ENV LD_LIBRARY_PATH=/lib64:/usr/lib64

# Switch back to astro user
USER 50000
WORKDIR /home/astro
EXPOSE 8686
ENTRYPOINT ["/usr/local/bin/vector"]
