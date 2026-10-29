# Network and database troubleshooting image for support engineers.
# Holds the tools the CRE runbooks run inside a short-lived debug pod
# (DNS, TCP/TLS checks, packet capture, test listeners, psql).

FROM quay.io/astronomer/ap-base:2026.10.26

# Runs as root on purpose: tcpdump and raw-socket tools need it, and the pod is
# only started by hand for troubleshooting, never as part of a workload.
USER 0

RUN apk add --no-cache \
      bash curl wget openssl jq \
      bind-tools netcat-openbsd nmap socat \
      iproute2 iputils tcpdump \
      python-3.13 postgresql-18-client

CMD ["sleep", "infinity"]
