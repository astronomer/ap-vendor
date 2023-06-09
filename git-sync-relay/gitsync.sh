#!/bin/sh

set -e

GIT_SSH_COMMAND="ssh -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o KbdInteractiveDevices=no"

if [ ! -d "$GIT_SYNC_ROOT" ]; then
  echo "Error: GIT_SYNC_ROOT ${GIT_SYNC_ROOT} does not exist!"
  exit 1
fi

if [ -n "$(ls -A "$GIT_SYNC_ROOT")" ]; then
  echo "Error: GIT_SYNC_ROOT ${GIT_SYNC_ROOT} is not empty."

  if grep -qF "$GIT_SYNC_REPO" "$GIT_SYNC_ROOT/.git/config"; then
    echo "repo is in .git/config, continue"
  else
    echo "repo is not in .git/config, cleaning the directory..."
    rm -rf "$GIT_SYNC_ROOT"
  fi
fi


if [ -n "$GIT_SYNC_SSH" ] && [ "true" = "$GIT_SYNC_SSH" ]; then
  GIT_SSH_COMMAND="$GIT_SSH_COMMAND -i $GIT_SSH_KEY_FILE"

  if [ -n "$GIT_KNOWN_HOSTS" ] && [ "true" = "$GIT_KNOWN_HOSTS" ]; then
    GIT_SSH_COMMAND="$GIT_SSH_COMMAND -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$GIT_SSH_KNOWN_HOSTS_FILE"
  else
    GIT_SSH_COMMAND="$GIT_SSH_COMMAND -o StrictHostKeyChecking=yes"
  fi

  export GIT_SSH_COMMAND
fi

cd "$GIT_SYNC_ROOT"

# Clone the repo for the first time
if [ ! -f "$GIT_SYNC_ROOT/.git/config" ]; then
  if [ "$GIT_SYNC_DEPTH" -gt 0 ]; then
    git clone --depth "$GIT_SYNC_DEPTH" --branch "$GIT_SYNC_BRANCH" "$GIT_SYNC_REPO" .
  else
    git clone --branch "$GIT_SYNC_BRANCH" "$GIT_SYNC_REPO" .
  fi
else
  echo "REPO already exists. Skipping clone"
fi

while true; do
  git fetch origin
  git reset --hard "origin/$GIT_SYNC_BRANCH"
  sleep "$GIT_SYNC_WAIT"
done
