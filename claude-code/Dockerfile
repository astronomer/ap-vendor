FROM quay.io/astronomer/ap-base:2025.11.3 AS builder
USER root
RUN apk add --no-cache curl jq
ARG VERSION=2.0.47
ARG TARGETARCH
WORKDIR /tmp
# Download and verify Claude Code binary
# Maps Docker ARCH to Claude release platform names
RUN if [ "$TARGETARCH" != "amd64" ]; then \
       echo "Unsupported architecture: $TARGETARCH"; exit 1; \
    fi && \
    PLATFORM="linux-x64" && \
    # Download manifest
    # URL derived from official install script: https://claude.ai/install.sh (the storage URL could change in the future)
    curl -fsSL "https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/${VERSION}/manifest.json" -o manifest.json && \
    # Extract checksum
    CHECKSUM=$(jq -r ".platforms[\"$PLATFORM\"].checksum // empty" manifest.json) && \
    if [ -z "$CHECKSUM" ]; then echo "Checksum not found"; exit 1; fi && \
    # Download binary
    curl -fsSL -o claude "https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/${VERSION}/${PLATFORM}/claude" && \
    # Verify checksum
    echo "$CHECKSUM  claude" | sha256sum -c - && \
    chmod +x claude

FROM quay.io/astronomer/ap-base:2025.11.3
LABEL maintainer="Astronomer <humans@astronomer.io>"
USER root
# Install runtime dependencies for Claude Code
RUN apk add --no-cache git ripgrep
COPY --from=builder /tmp/claude /usr/local/bin/claude
ENV HOME=/home/claude
WORKDIR /home/claude
RUN mkdir -p /home/claude && chown 65534:65534 /home/claude
USER 65534:65534
# Entrypoint set to claude binary to allow running as an executable
ENTRYPOINT ["/usr/local/bin/claude"]
