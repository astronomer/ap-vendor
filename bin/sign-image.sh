#!/usr/bin/env bash
set -euo pipefail

# Registries to sign images in
REGISTRIES=(
  "quay.io astronomer"
  "docker.io astronomerinc"
  "astrocrpublic.azurecr.io astronomer"
  "astrocr.azurecr.io astronomer"
)

usage() {
  echo "Script to sign Docker images using cosign"
  echo "Usage: sign-image.sh <directory> <tag>"
  echo "Examples:"
  echo "sign-image.sh redis latest"
}

setup_keys() {
  echo "Setting up cosign keys..."
  echo "-----BEGIN ENCRYPTED SIGSTORE PRIVATE KEY-----" > /tmp/cosign.key
  echo "$COSIGN_PRIVATE_KEY" |
    sed 's/.*BEGIN ENCRYPTED SIGSTORE PRIVATE KEY----- \(.*\) -----END.*/\1/' |
    tr -d ' ' | fold -w 64 >> /tmp/cosign.key
  echo "-----END ENCRYPTED SIGSTORE PRIVATE KEY-----" >> /tmp/cosign.key

  echo "-----BEGIN PUBLIC KEY-----" > /tmp/cosign.pub
  echo "$COSIGN_PUBLIC_KEY" |
    sed 's/.*BEGIN PUBLIC KEY----- \(.*\) -----END.*/\1/' |
    tr -d ' ' | fold -w 64 >> /tmp/cosign.pub
  echo "-----END PUBLIC KEY-----" >> /tmp/cosign.pub
}

sign_image() {
  local registry=$1
  local repository=$2
  local directory=$3
  local tag=$4
  local image_path="$registry/$repository/ap-$directory:$tag"
  
  echo "Signing image: $image_path"
  echo "$COSIGN_PASSWORD" | cosign sign --yes --key /tmp/cosign.key "$image_path"
  
  echo "Verifying image: $image_path"
  cosign verify --key /tmp/cosign.pub "$image_path"
}

mark_as_signed() {
  mkdir -p /tmp/workspace/signing
  echo "SIGNED=true" > /tmp/workspace/signing/status.txt
  echo "Images successfully signed at $(date)" >> /tmp/workspace/signing/status.txt
}

cleanup_keys() {
  echo "Cleaning up key files..."
  rm -f /tmp/cosign.key /tmp/cosign.pub
}

if [[ $# -eq 2 ]]; then
  DIRECTORY=$1
  TAG=$2
  setup_keys
  for registry_repo in "${REGISTRIES[@]}"; do
    read -r registry repository <<< "$registry_repo"
    sign_image "$registry" "$repository" "$DIRECTORY" "$TAG"
  done
  mark_as_signed
  cleanup_keys
elif [[ $# -eq 4 ]]; then
  setup_keys
  sign_image "$1" "$2" "$3" "$4"
  mark_as_signed
  cleanup_keys
else
  usage
  exit 1
fi