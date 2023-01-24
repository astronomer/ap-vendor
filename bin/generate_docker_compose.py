#!/usr/bin/env python3
"""This script is used to create the docker-compose file so that we can stay
DRY."""
import os
from pathlib import Path

import yaml
from jinja2 import Template

dirs_to_skip = [
    ".circleci",
    ".git",
    ".github",
    ".idea",
    ".pytest_cache",
    "bin",
    "requirements",
]


def list_docker_dirs(path):
    all_dirs = set(next(os.walk(path))[1])
    docker_image_dirs = all_dirs.difference(dirs_to_skip)
    return sorted(docker_image_dirs)


def read_test_config(project_directory, docker_image_dirs):
    docker_image_config = {}

    for docker_image_dir in docker_image_dirs:
        test_config_path = project_directory / docker_image_dir / "test.yaml"

        # Reading yaml file
        with open(test_config_path) as file:
            config = yaml.safe_load(file)

        # Reading docker config
        if config is not None and "docker" in config:
            docker_config = config["docker"]
            docker_image_config[docker_image_dir] = docker_config
        else:
            docker_image_config[docker_image_dir] = []

    return docker_image_config


def main():
    """Render the Jinja2 template file."""
    project_directory = Path(__file__).parent.parent
    docker_compose_template_path = project_directory / "docker-compose.yaml.j2"
    docker_compose_path = project_directory / "docker-compose.yaml"

    with docker_compose_template_path.open() as docker_compose_config_template:
        templated_file_content = docker_compose_config_template.read()

    docker_image_dirs = list_docker_dirs(project_directory)
    docker_configs = read_test_config(project_directory, docker_image_dirs)

    template = Template(templated_file_content)
    config = template.render(docker_images=docker_configs)
    warning_header = (
        "# Warning: automatically generated file\n"
        + "# Please edit docker-compose.yaml.j2, then run bin/generate_docker_compose.py\n"
    )
    with docker_compose_path.open("w") as circle_ci_config_file:
        circle_ci_config_file.write(warning_header)
        circle_ci_config_file.write(config + "\n")


if __name__ == "__main__":
    main()
