#!/bin/sh

set -e

if [ ! -d "$GIT_SYNC_ROOT" ]; then
  echo "Error: GIT_SYNC_ROOT ${GIT_SYNC_ROOT} is not exists!"
  exit 1
fi

if [ -n "$(ls -A "$GIT_SYNC_ROOT")" ]; then
  echo "Error: GIT_SYNC_ROOT ${GIT_SYNC_ROOT} is not Empty."
  exit 1
fi

if [ -n "$GIT_SYNC_SSH" ] && [ "true" = "$GIT_SYNC_SSH" ]; then
  cp "$GIT_SSH_KEY_FILE" "$HOME/.ssh/$GIT_SSH_KEY_FILE"
fi

if [ -n "$GIT_KNOWN_HOSTS" ] && [ "true" = "$GIT_KNOWN_HOSTS" ]; then
  cp "$GIT_SSH_KNOWN_HOSTS_FILE" "$HOME/.ssh/$GIT_SSH_KNOWN_HOSTS_FILE"
fi

cd "$GIT_SYNC_ROOT"

# Clone the repo for the first time
if [ "$GIT_SYNC_DEPTH" -gt 0 ]; then
  git clone --depth "$GIT_SYNC_DEPTH" --branch "$GIT_SYNC_BRANCH" "$GIT_SYNC_REPO" .
else
  git clone --branch "$GIT_SYNC_BRANCH" "$GIT_SYNC_REPO" .
fi

while true; do
  git fetch origin
  git reset --hard "origin/$GIT_SYNC_BRANCH"
  sleep "$GIT_SYNC_WAIT"
done
