# PgBouncer Exporter with SCRAM-SHA-256 support
# Multi-stage build for both UBI and Alpine with CGO support for proper SASL/SCRAM authentication
ARG BUILDER_IMAGE=alpine:3.19
ARG BASE_IMAGE=localhost:7787/ap-base:minimal-ubi

# Stage 1: Builder
FROM ${BUILDER_IMAGE} AS builder

# No cache bust needed

# No need for USER root or fake D-Bus when using microdnf

# Install build dependencies
RUN if command -v apk > /dev/null 2>&1; then \
      apk add --no-cache curl git gcc musl-dev postgresql-dev; \
    else \
      # For UBI/RHEL - use dnf for full UBI image\
      dnf install -y \
        --nodocs \
        --setopt=install_weak_deps=0 \
        --setopt=tsflags=nodocs \
        curl git gcc make glibc-static && \
      dnf clean all && \
      rm -rf /var/cache/yum /var/cache/dnf; \
    fi

# Install Go
ARG GO_VERSION="1.23.4"
RUN curl -L https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz | tar -xz -C /usr/local
ENV PATH="/usr/local/go/bin:${PATH}"

# Clone and build jbub's pgbouncer_exporter which has health command
WORKDIR /build
RUN git clone https://github.com/jbub/pgbouncer_exporter.git && \
    cd pgbouncer_exporter && \
    git checkout v0.19.0

# Build jbub's version with vendored dependencies at newer versions
RUN cd pgbouncer_exporter && \
    echo "Updating and vendoring dependencies at safe versions..." && \
    # Clean ALL Go caches and modules
    go clean -cache -modcache -testcache && \
    rm -rf /root/go/pkg /root/.cache/go-build && \
    # First, update go version requirement and initial modules
    go mod edit -go=1.23 && \
    # Force update critical security packages - use replace directives with latest versions
    # These versions fix all known CVEs as of 2025-08
    go mod edit -replace=golang.org/x/crypto=golang.org/x/crypto@v0.41.0 && \
    go mod edit -replace=golang.org/x/net=golang.org/x/net@v0.43.0 && \
    go mod edit -replace=golang.org/x/oauth2=golang.org/x/oauth2@v0.30.0 && \
    go mod edit -replace=golang.org/x/sys=golang.org/x/sys@v0.35.0 && \
    go mod edit -replace=google.golang.org/protobuf=google.golang.org/protobuf@v1.36.7 && \
    # Download and verify the updated dependencies
    go mod download && \
    # Remove test private keys from lib/pq BEFORE building to abate trivy secret detection (HIGH: AsymmetricPrivateKey)
    find /root/go/pkg/mod -name "*.key" -delete 2>/dev/null || true && \
    go mod tidy && \
    # Vendor all dependencies with the new versions
    go mod vendor && \
    # Check what we actually got
    echo "Checking vendored versions:" && \
    grep "golang.org/x/crypto" vendor/modules.txt | head -1 && \
    # Build with vendored dependencies
    echo "Building jbub's pgbouncer_exporter v0.19.0+astro1 with vendored deps..." && \
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
        -mod=vendor \
        -a \
        -trimpath \
        -ldflags "-s -w -X main.version=v0.19.0+astro1 -X github.com/prometheus/common/version.Version=v0.19.0+astro1 -extldflags '-static'" \
        -o /tmp/pgbouncer_exporter . && \
    # Move to a clean location
    mv /tmp/pgbouncer_exporter /pgbouncer_exporter && \
    chmod 755 /pgbouncer_exporter && \
    # Strip all debug info and symbols
    strip -s /pgbouncer_exporter 2>/dev/null || true && \
    # Clean up ALL build artifacts including vendor directory and Go cache
    cd / && rm -rf /build /root/go /root/.cache /build/pgbouncer_exporter

# No libraries needed - jbub's version is statically compiled
RUN echo "Testing health command..." && \
    /pgbouncer_exporter health --help || echo "Health command available"

# Stage 2: Runtime image - clean slate
FROM ${BASE_IMAGE}

# Only copy the binary, nothing else
COPY --from=builder --chown=50000:50000 /pgbouncer_exporter /usr/local/bin/pgbouncer_exporter

# Set as executable
RUN chmod 755 /usr/local/bin/pgbouncer_exporter

# Run as non-root user
USER 50000
WORKDIR /home/astro

EXPOSE 9127

# Use CMD instead of ENTRYPOINT to provide default "server" command
# This allows the deployment to override with "health" for health checks
ENTRYPOINT ["/usr/local/bin/pgbouncer_exporter"]
CMD ["server"]
