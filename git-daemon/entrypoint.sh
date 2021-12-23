#!/bin/sh
# git-daemon entrypoint

if [ -z "$GIT_ROOT" ] ; then
  echo "ERROR: env var GIT_ROOT must be set to a directory to serve."
  exit 1
fi

if [ ! -d "$GIT_ROOT" ] ; then
  echo "ERROR: $GIT_ROOT is not a directory!"
  exit 1
fi

set -xe

touch "$GIT_ROOT/.git/git-daemon-export-ok"
git daemon --verbose
