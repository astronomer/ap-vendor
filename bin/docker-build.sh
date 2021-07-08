#!/usr/bin/env bash
set -xe

[[ $# -eq 2 ]] || exit 1

labels=(
    "--label=io.astronomer.build.branch=$CIRCLE_BRANCH"
    "--label=io.astronomer.build.date=$(date +%F)"
    "--label=io.astronomer.build.job.id=$CIRCLE_BUILD_NUM"
    "--label=io.astronomer.build.job.name=$CIRCLE_JOB"
    "--label=io.astronomer.build.repo=$CIRCLE_REPOSITORY_URL"
    "--label=io.astronomer.build.sha=$CIRCLE_SHA1"
    "--label=io.astronomer.build.unixtime=$(date +%s)"
    "--label=io.astronomer.build.url=$CIRCLE_BUILD_URL"
    "--label=io.astronomer.build.workflow.id=$CIRCLE_WORKFLOW_ID"
)

if ! [[ "$CIRCLE_BRANCH" =~ ^(master|main)$ ]] ; then
    labels+=( "--label=quay.expires-after=8w" )
fi

project_path="$1"
image_name="$2"
docker build \
    --pull \
    --platform linux/amd64 \
    --tag "$image_name" \
    --file "$project_path"/Dockerfile \
    --build-arg BUILD_NUMBER="$CIRCLE_BUILD_NUM" \
    "${labels[@]}" \
    "$project_path"

docker save -o "$image_name.tar" "$image_name"
docker inspect "$image_name"
