#!/usr/bin/env bash
set -xe

[[ $# -eq 2 ]] || exit 1
docker_repository="$1" # EG: "astronomer" in "quay.io/astronomer"
image_name="$2" # EG: "cat-pic-downloader" in "quay.io/astronomer/cat-pic-downloader"
comma_separated_tag_list="$3" # EG: alpine,latest,main,2021-07
docker_registry="$4" # Must be quay.io or docker.io

case "$docker_registry" in
    quay.io)
        function docker_tag_exists() {
            curl --silent -f -lSL "https://quay.io/api/v1/repository/$1/tag/$2/images" > /dev/null
        }
        ;;
    docker.io)
        function docker_tag_exists() {
            curl --silent -f -lSL "https://index.docker.io/v1/repositories/$1/tags/$2" > /dev/null
        }
        ;;
    *) echo "ERROR: Wrong docker_registry given." ; exit 1 ;;
esac

function tag_and_push() {
    docker tag "${image_name}" "${docker_registry}/${docker_repository}/${image_name}:$1"
    echo DEBUG docker push "${docker_registry}/${docker_repository}/${image_name}:$1"
}

comma_separated_tag_list="${CIRCLE_BRANCH},"

if ! [[ "$CIRCLE_BRANCH" =~ ^(master|main)$ ]] ; then
    comma_separated_tag_list="latest,${comma_separated_tag_list}"
fi

for tag in ${comma_separated_tag_list//,/ } ; do
    # If the tag looks starts with "v" then a digit, remove the "v"
    [[ "$tag" =~ ^v[0-9] ]] && tag="${tag/v/}"

    if docker_tag_exists "${docker_repository}/${image_name}" "${tag}" ; then
        if [[ "$tag" == "latest" ]]; then
            tag_and_push "$tag"
        else
            echo "This docker tag already exists. Skipping the Docker push!"
        fi
    else
        tag_and_push "$tag"
    fi
done
