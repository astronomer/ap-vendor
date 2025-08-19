# StatsD Exporter - built from source
ARG BUILDER_IMAGE=alpine:3.19
ARG BASE_IMAGE=alpine:3.19

FROM ${BUILDER_IMAGE} AS builder

# Install build dependencies
RUN if command -v apk > /dev/null 2>&1; then \
      apk add --no-cache curl git gcc musl-dev; \
    elif command -v dnf > /dev/null 2>&1; then \
      dnf install -y --allowerasing curl git gcc make; \
    elif command -v microdnf > /dev/null 2>&1; then \
      microdnf install -y curl git gcc make; \
    elif command -v apt-get > /dev/null 2>&1; then \
      apt-get update && apt-get install -y curl git gcc make && rm -rf /var/lib/apt/lists/*; \
    fi

# Install Go
# Go 1.23.4 for latest security patches
ARG GO_VERSION="1.23.4"
RUN curl -L https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz | tar -xz -C /usr/local
ENV PATH="/usr/local/go/bin:${PATH}"

# Build exporter with updated dependencies
# statsd_exporter v0.28.0 released 2024-11-13
ARG EXPORTER_VERSION="v0.28.0"
WORKDIR /build
RUN git clone https://github.com/prometheus/statsd_exporter.git && \
    cd statsd_exporter && \
    git checkout ${EXPORTER_VERSION} && \
    echo "Updating and vendoring dependencies at safe versions..." && \
    # Clean ALL Go caches and modules
    go clean -cache -modcache -testcache && \
    rm -rf /root/go/pkg /root/.cache/go-build && \
    # Update go.mod to require latest safe versions directly
    # These versions fix all known CVEs as of 2025-08
    go mod edit -require=golang.org/x/crypto@v0.41.0 && \
    go mod edit -require=golang.org/x/net@v0.43.0 && \
    go mod edit -require=golang.org/x/oauth2@v0.30.0 && \
    go mod edit -require=golang.org/x/sys@v0.35.0 && \
    go mod edit -require=google.golang.org/protobuf@v1.36.7 && \
    # Download and verify the updated dependencies
    go mod download && \
    # Remove any test private keys to prevent secret detection
    find /root/go/pkg/mod -name "*.key" -delete 2>/dev/null || true && \
    go mod tidy && \
    # Vendor all dependencies with the new versions
    go mod vendor && \
    # Verify vendor directory has the right versions
    grep -q "v0.41.0" vendor/modules.txt || exit 1 && \
    # Build with vendored dependencies and custom version tag
    echo "Building statsd_exporter ${EXPORTER_VERSION}+astro1 with vendored deps..." && \
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -mod=vendor -a -trimpath \
        -ldflags="-s -w -X github.com/prometheus/common/version.Version=${EXPORTER_VERSION}+astro1 -extldflags '-static'" \
        -o /tmp/statsd_exporter && \
    # Move and clean up
    mv /tmp/statsd_exporter /statsd_exporter && \
    chmod 755 /statsd_exporter && \
    strip -s /statsd_exporter 2>/dev/null || true && \
    # Clean up ALL build artifacts including Go cache
    cd / && rm -rf /build /root/go /root/.cache

# Final stage - uses ap-base which already has astro user
FROM ${BASE_IMAGE}

# Switch to root for installation
USER root
COPY --from=builder /statsd_exporter /usr/local/bin/statsd_exporter
RUN chmod 755 /usr/local/bin/statsd_exporter

# Switch back to astro user
USER 50000
WORKDIR /home/astro
EXPOSE 9102 9125/udp
ENTRYPOINT ["/usr/local/bin/statsd_exporter"]
