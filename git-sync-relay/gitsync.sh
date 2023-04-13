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
