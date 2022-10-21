#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import date
from pathlib import Path

import docker
from docker.errors import APIError
from packaging.version import parse as semver

root_directory = Path(__file__).parent.parent

docker_labels = {
    "io.astronomer.build.branch": os.getenv("CIRCLE_BRANCH"),
    "io.astronomer.build.job.id": os.getenv("CIRCLE_BUILD_NUM"),
    "io.astronomer.build.job.name": os.getenv("CIRCLE_JOB"),
    "io.astronomer.build.repo": os.getenv("CIRCLE_REPOSITORY_URL"),
    "io.astronomer.build.sha": os.getenv("CIRCLE_SHA1"),
    "io.astronomer.build.url": os.getenv("CIRCLE_BUILD_URL"),
    "io.astronomer.build.workflow.id": os.getenv("CIRCLE_WORKFLOW_ID"),
}


def login_registry(docker_client: docker, registry: str, username: str, password: str):
    # Login to Registry
    print("INFO: Login to: " + registry)
    docker_client.login(username=username, password=password, registry=registry)

    return docker_client


def get_image_tags(project_path: str):
    docker_image_path = root_directory / project_path

    try:
        with open(docker_image_path / "version.txt") as version_file:
            versions_text = version_file.read().strip()
            versions = versions_text.split(",")

            for version in versions:

                if not semver(version).release:
                    raise Exception(
                        f"ERROR: No valid semver found in {docker_image_path}/version.txt"
                    )

            return versions

    except FileNotFoundError:
        raise Exception(f"ERROR: version.txt not found in {docker_image_path}")


def validate_tags(
    docker_client: docker,
    registry: str,
    repository: str,
    image: str,
    tags: list,
    override_tags: bool,
):
    docker_image_uri = registry + "/" + repository + "/" + image

    if override_tags:
        print(
            "INFO: Overwrite is set to True. If the tag already exists it will be overwritten."
        )
        return tags
    else:

        final_tags = []
        for tag in tags:

            if tag == "latest":
                print("INFO: The image tag is `latest`. It will override.")
                final_tags.append(tag)
            else:
                try:
                    docker_client.images.get_registry_data(
                        name=(docker_image_uri + ":" + tag)
                    )

                    print(
                        f"INFO: The docker tag {docker_image_uri}:{tag} already exists. Skipping the Docker push!"
                    )
                except APIError as dokerAPIError:
                    print(
                        f"INFO: Docker tag {docker_image_uri}:{tag} not found on server. It will be added to the push list."
                    )
                    final_tags.append(tag)

        return final_tags


def build(docker_client: docker, project_path: str, image: str):
    today = date.today()
    docker_labels["io.astronomer.build.date"] = today.strftime("%Y-%m-%d")
    docker_labels["io.astronomer.build.unixtime"] = today.strftime("%s")

    image_tag = os.getenv("CIRCLE_SHA1")

    if "master" != os.getenv("CIRCLE_BRANCH") or "main" != os.getenv("CIRCLE_BRANCH"):
        docker_labels["quay.expires-after"] = "8w"

    # Build Docker Image
    print("INFO: Now building docker image: " + str(root_directory / project_path))
    docker_image_resp = docker_client.images.build(
        pull=True,
        platform="linux/amd64",
        path=project_path,
        tag=image,
        nocache=True,
        dockerfile=(root_directory / project_path / "Dockerfile"),
        buildargs={"BUILD_NUMBER": os.getenv("CIRCLE_BUILD_NUM")},
        labels=docker_labels,
        quiet=False,
    )

    # Printing Docker Image Build Progress
    for line in docker_image_resp[1]:
        for key, value in line.items():
            if key == "stream":
                text = value.strip()
                if text:
                    print(text)

    docker_image = docker_image_resp[0]

    # Tagging Docker Image
    is_tagged = docker_image.tag(repository=image, tag=image_tag)

    if is_tagged is False:
        raise Exception(f"Error Image {image} is not tagged with {image_tag}.")

    # Save Docker Image
    docker_image_save_path = f"{image}.tar"
    docker_image_to_save = docker_client.images.get(image + ":" + image_tag)
    print("INFO: Saving docker image: " + docker_image_save_path)
    f = open(docker_image_save_path, "wb")
    for chunk in docker_image_to_save.save(named=True):
        f.write(chunk)
    f.close()

    return docker_image


def push(
    docker_client: docker,
    registry: str,
    repository: str,
    image: str,
    tags: list,
):
    try:
        docker_image_uri = registry + "/" + repository + "/" + image
        image_tag = os.getenv("CIRCLE_SHA1")

        for tag in tags:

            docker_image = docker_client.images.get(image + ":" + image_tag)

            print(f"Tagging Image {image}:{image_tag} --> {docker_image_uri}:{tag}.")
            is_tagged = docker_image.tag(repository=docker_image_uri, tag=tag)

            if is_tagged is False:
                raise Exception(
                    f"Getting error while tagging Image {image}:{image_tag} --> {docker_image_uri}:{tag}."
                )

            print(f"INFO: Pushing docker image: {docker_image_uri}:{tag}")

            push_resp_generator = docker_client.images.push(
                repository=docker_image_uri, tag=tag, stream=True, decode=True
            )

            # Printing Push Progress
            for line in push_resp_generator:
                if "status" in line and "progress" in line and "id" in line:
                    text = line["id"] + ": " + line["status"] + " " + line["progress"]
                    print(text)
                elif "status" in line and "id" in line:
                    text = line["id"] + ": " + line["status"]
                    print(text)
                elif "status" in line:
                    text = line["status"]
                    print(text)

            if "error" in line:
                raise Exception(line["errorDetail"]["message"])
            else:
                print(f"INFO: Pushed docker image: {docker_image_uri}:{tag}")
                return True

    except APIError as dokerAPIError:
        print("ERROR: Error pushing docker image", file=sys.stderr)
        raise dokerAPIError


def main():
    arg_parser = argparse.ArgumentParser(
        description="A script to handle docker operations."
    )

    arg_parser.add_argument("operation", type=str)
    arg_parser.add_argument("--project_path", type=str)
    arg_parser.add_argument("--registry", type=str)
    arg_parser.add_argument("--username", type=str)
    arg_parser.add_argument("--password", type=str)
    arg_parser.add_argument("--repository", type=str)
    arg_parser.add_argument("--image", type=str)
    arg_parser.add_argument("--tags", type=str, default=None)
    arg_parser.add_argument("--override_tags", type=str, default="false")

    args = arg_parser.parse_args()

    # Setting up Docker Client
    docker_client = docker.from_env()

    if "build" == args.operation:

        if args.project_path is None:
            raise Exception("Error: Project Path is required.")
        elif args.image is None:
            raise Exception("Error: Image name is required.")

        build(
            docker_client=docker_client,
            project_path=args.project_path,
            image=args.image,
        )

    elif "validate_tags" == args.operation:

        tags = args.tags
        override_tags = False

        if "true" == args.override_tags.lower():
            override_tags = True

        if args.project_path is None:
            raise Exception("Error: Project Path is required.")
        elif args.registry is None:
            raise Exception("Error: Registry is required.")
        elif args.username is None:
            raise Exception("Error: Registry Username is required.")
        elif args.password is None:
            raise Exception("Error: Registry Password is required.")
        elif args.repository is None:
            raise Exception("Error: Repository is required.")
        elif args.image is None:
            raise Exception("Error: Image name is required.")

        if tags is None:
            tags = get_image_tags(project_path=args.project_path)

        # Login to registry
        docker_client = login_registry(
            docker_client=docker_client,
            registry=args.registry,
            username=args.username,
            password=args.password,
        )

        final_tags = validate_tags(
            docker_client=docker_client,
            registry=args.registry,
            repository=args.repository,
            image=args.image,
            tags=tags,
            override_tags=override_tags,
        )

        print(f"INFO: Input tags list: {tags}")
        print(f"INFO: Final tags list: {final_tags}")

        if len(final_tags) == len(tags):
            print("INFO: All tags are valid.")
        else:
            raise Exception(f"ERROR: Looks like one or many tag(s) already exists!")

    elif "push" == args.operation:

        tags = args.tags
        override_tags = False

        if "true" == args.override_tags.lower():
            override_tags = True

        if args.project_path is None:
            raise Exception("Error: Project Path is required.")
        elif args.registry is None:
            raise Exception("Error: Registry is required.")
        elif args.username is None:
            raise Exception("Error: Registry Username is required.")
        elif args.password is None:
            raise Exception("Error: Registry Password is required.")
        elif args.repository is None:
            raise Exception("Error: Repository is required.")
        elif args.image is None:
            raise Exception("Error: Image name is required.")

        if tags is None:
            tags = get_image_tags(project_path=args.project_path)

        # Login to registry
        docker_client = login_registry(
            docker_client=docker_client,
            registry=args.registry,
            username=args.username,
            password=args.password,
        )

        final_tags = validate_tags(
            docker_client=docker_client,
            registry=args.registry,
            repository=args.repository,
            image=args.image,
            tags=tags,
            override_tags=override_tags,
        )

        push(
            docker_client=docker_client,
            registry=args.registry,
            repository=args.repository,
            image=args.image,
            tags=final_tags,
        )
    else:
        raise Exception("Error: No operation match to execute!")

    docker_client.close()


if __name__ == "__main__":
    main()
