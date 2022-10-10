#!/usr/bin/env python3
import argparse
import os
from datetime import date
from pathlib import Path

import docker
from docker.errors import APIError

project_directory = Path(__file__).parent.parent

docker_labels = {
    "io.astronomer.build.branch": os.getenv("CIRCLE_BRANCH", "default_branch"),
    "io.astronomer.build.job.id": os.getenv("CIRCLE_BUILD_NUM", "default_build_num"),
    "io.astronomer.build.job.name": os.getenv("CIRCLE_JOB", "default_job"),
    "io.astronomer.build.repo": os.getenv("CIRCLE_REPOSITORY_URL", "default_repo_url"),
    "io.astronomer.build.sha": os.getenv("CIRCLE_SHA1", "default_sha1"),
    "io.astronomer.build.url": os.getenv("CIRCLE_BUILD_URL", "default_build_url"),
    "io.astronomer.build.workflow.id": os.getenv(
        "CIRCLE_WORKFLOW_ID", "default_workflow_id"
    ),
}


def build(docker_client: docker, project_path: str, image: str):
    today = date.today()
    docker_labels["io.astronomer.build.date"] = today.strftime("%Y-%m-%d")
    docker_labels["io.astronomer.build.unixtime"] = today.strftime("%s")

    image_tag = os.getenv("CIRCLE_SHA1", "circleci_sha1")

    if "master" != os.getenv("CIRCLE_BRANCH") or "main" != os.getenv(
        "CIRCLE_BRANCH", "default_branch"
    ):
        docker_labels["quay.expires-after"] = "8w"

    # Build Docker Image
    print("INFO: Now building docker image: " + str(project_directory / project_path))
    docker_image_resp = docker_client.images.build(
        pull=True,
        platform="linux/amd64",
        path=project_path,
        tag=image,
        nocache=True,
        dockerfile=(project_directory / project_path / "Dockerfile"),
        buildargs={"BUILD_NUMBER": os.getenv("CIRCLE_BUILD_NUM", "default_build_num")},
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
    username: str,
    password: str,
    repository: str,
    image: str,
    tag: str,
):
    try:
        docker_image = registry + "/" + repository + "/" + image

        print("INFO: Login to: " + registry)
        docker_client.login(username=username, password=password, registry=registry)

        # Check for tag exist already on server
        docker_image_tag_exists = False
        if tag != "latest":
            try:
                docker_client.images.get_registry_data(name=(docker_image + ":" + tag))
                docker_image_tag_exists = True
            except APIError as dokerAPIError:
                print("INFO: Image not found on server.")
                docker_image_tag_exists = False
            except:
                raise Exception("Error: Unable to read registry...")

        if docker_image_tag_exists:
            print(
                "INFO: The docker tag {docker_image}:{tag} already exists. Skipping the "
                "Docker push!".format(docker_image=docker_image, tag=tag)
            )
        else:

            print("INFO: Pushing docker image: " + docker_image + ":" + tag)

            push_resp_generator = docker_client.images.push(
                repository=docker_image, tag=tag, stream=True, decode=True
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
                print("INFO: Pushed docker image: " + docker_image + ":" + tag)
                return True

    except APIError as dokerAPIError:
        print("ERROR: Error pushing docker image")
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
    arg_parser.add_argument("--tag", type=str)

    args = arg_parser.parse_args()

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

    elif "push" == args.operation:

        if args.registry is None:
            raise Exception("Error: Registry is required.")
        elif args.username is None:
            raise Exception("Error: Registry Username is required.")
        elif args.password is None:
            raise Exception("Error: Registry Password is required.")
        elif args.repository is None:
            raise Exception("Error: Repository is required.")
        elif args.image is None:
            raise Exception("Error: Image name is required.")
        elif args.tag is None:
            raise Exception("Error: Image tag is required.")

        push(
            docker_client=docker_client,
            registry=args.registry,
            username=args.username,
            password=args.password,
            repository=args.repository,
            image=args.image,
            tag=args.tag,
        )
    else:
        raise Exception("Error: No operation match to execute!")

    docker_client.close()


if __name__ == "__main__":
    main()
