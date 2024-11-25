#!/usr/bin/env bash

[ "$#" == 1 ] || { echo "ERROR: Must give exactly one thing to scan, in the form of an ap-vendor directory." ; exit 1 ; }
[ -f /etc/os-release ] && cat /etc/os-release

GIT_ROOT="$(git -C "${0%/*}" rev-parse --show-toplevel)"
scan_target="$1"

set +exo pipefail

trivy_args=(
  "--cache-dir" "/tmp/workspace/trivy-cache"
  "image"
  "--ignore-unfixed" "-s" "HIGH,CRITICAL"
  "--exit-code" "1"
  "--no-progress"
)

ignore_file="${GIT_ROOT}/${scan_target}/trivyignore"
if [ -f "${ignore_file}" ]; then
  trivy_args+=(--ignorefile "${ignore_file}")
fi

config_file="${GIT_ROOT}/${scan_target}/trivy.yaml"
if [ -f "${config_file}" ]; then
  trivy_args+=(--config "${config_file}")
fi

trivy "${trivy_args[@]}" "ap-${scan_target}:${CIRCLE_SHA1}" > "${GIT_ROOT}/trivy-output.txt"
exit_code=$?

cat "${GIT_ROOT}/trivy-output.txt"

# Trivy cannot detect vulnerabilities not installed by package managers (EG: busybox, buildroot, make install):
# - https://github.com/aquasecurity/trivy/issues/481 2020-04-30
if grep -q -i 'OS is not detected' trivy-output.txt ; then
  echo "Skipping trivy scan because of unsupported OS"
  exit 0
fi

exit "${exit_code}"
