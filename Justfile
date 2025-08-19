# Justfile for building minimal container images
# Usage: just build-all [alpine|ubi]

# Default values
registry := env_var_or_default("REGISTRY", "192.168.1.243:5000")
platform := env_var_or_default("PLATFORM", "linux/amd64")
tag := env_var_or_default("TAG", "minimal")

# Set base image variables based on type
_base-vars base_type:
	#!/usr/bin/env bash
	case "{{base_type}}" in
	  alpine)
	    echo "BASE_IMAGE=alpine:3.19"
	    echo "BUILDER_IMAGE=alpine:3.19"
	    echo "PACKAGE_MANAGER=apk"
	    echo "PACKAGE_NAMING_SCHEME=alpine"
	    ;;
	  ubi)
	    echo "BASE_IMAGE=registry.access.redhat.com/ubi10/ubi-micro:10.0-1747317009"
	    echo "BUILDER_IMAGE=registry.access.redhat.com/ubi10/ubi:10.0-1747220028"
	    echo "PACKAGE_MANAGER=dnf"
	    echo "PACKAGE_NAMING_SCHEME=redhat"
	    ;;
	  *)
	    echo "Invalid base type: {{base_type}}. Use 'alpine' or 'ubi'" >&2
	    exit 1
	    ;;
	esac

# Generic build function
_build component dockerfile base_type:
	#!/usr/bin/env bash
	set -euo pipefail
	eval "$(just _base-vars {{base_type}})"

	BASE_ARG="${BASE_IMAGE}"
	[[ "{{component}}" != "ap-base" ]] && BASE_ARG="{{registry}}/ap-base:{{tag}}-{{base_type}}"

	echo "Building {{component}} with {{base_type}}..."
	podman --cgroup-manager=cgroupfs build \
	  -f "{{component}}/{{dockerfile}}" \
	  --build-arg BASE_IMAGE="${BASE_ARG}" \
	  --build-arg BUILDER_IMAGE="${BUILDER_IMAGE}" \
	  --build-arg PACKAGE_MANAGER="${PACKAGE_MANAGER}" \
	  --build-arg PACKAGE_NAMING_SCHEME="${PACKAGE_NAMING_SCHEME}" \
	  -t "{{registry}}/{{component}}:{{tag}}-{{base_type}}" \
	  --platform "{{platform}}" \
	  "{{component}}"

# Build targets
build-all base_type="alpine": (build-base base_type) (build-components base_type)

build-base base_type="alpine": (_build "ap-base" "Dockerfile" base_type)

build-components base_type="alpine": (build-redis base_type) (build-vector base_type) (build-pgbouncer base_type) (build-pgbouncer-exporter base_type) (build-statsd-exporter base_type)

build-redis base_type="alpine": (_build "redis" "Dockerfile" base_type)

build-vector base_type="alpine": (_build "vector" "Dockerfile" base_type)

build-pgbouncer base_type="alpine": (_build "pgbouncer" "Dockerfile" base_type)

build-pgbouncer-exporter base_type="alpine": (_build "pgbouncer-exporter" "Dockerfile" base_type)

build-statsd-exporter base_type="alpine": (_build "statsd-exporter" "Dockerfile" base_type)

# Push all images to registry
push-all base_type="alpine":
	#!/usr/bin/env bash
	for component in ap-base redis vector pgbouncer pgbouncer-exporter statsd-exporter; do
	  echo "Pushing $component..."
	  podman push --tls-verify=false "{{registry}}/$component:{{tag}}-{{base_type}}"
	done

# Run smoke tests
test base_type="alpine":
	#!/usr/bin/env bash
	set -euo pipefail

	declare -A bins=(
	  ["vector"]="/usr/local/bin/vector"
	  ["pgbouncer"]="/usr/local/bin/pgbouncer"
	  ["pgbouncer-exporter"]="/usr/local/bin/pgbouncer_exporter"
	  ["statsd-exporter"]="/usr/local/bin/statsd_exporter"
	)

	for comp in "${!bins[@]}"; do
	  echo "Testing $comp..."
	  podman run --rm --read-only --tmpfs /tmp:rw,noexec,nosuid --user 4242 \
	    "{{registry}}/$comp:{{tag}}-{{base_type}}" \
	    ${bins[$comp]} --version 2>&1 | head -1 || echo "  Failed"
	done

# Clean up all images
clean base_type="alpine":
	#!/usr/bin/env bash
	for c in ap-base redis vector pgbouncer pgbouncer-exporter statsd-exporter; do
	  podman rmi "{{registry}}/$c:{{tag}}-{{base_type}}" 2>/dev/null || true
	done

# List built images
list:
	@podman images | grep "{{registry}}" | grep "{{tag}}"

# Default shows available commands
default:
	@just --list
