#!/usr/bin/env bash
# Script to check Cosign image signature status
set -euo pipefail

if [ "${SKIP_SIGNATURE_CHECK:-false}" = "true" ]; then
  echo "Skipping signature check as requested."
  exit 0
fi

if [ -f /tmp/workspace/signing/status.txt ]; then
  source /tmp/workspace/signing/status.txt
  if [ "${SIGNED:-false}" != "true" ]; then
    echo "Image was not properly signed. Aborting push."
    exit 1
  fi
else
  echo "Signing status file not found but checking required. Aborting push."
  exit 1
fi

echo "Signature validation passed."
exit 0