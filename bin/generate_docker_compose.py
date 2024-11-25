#!/usr/bin/env python3
"""This script is used to create the docker-compose file so that we can stay
DRY."""

from collections.abc import Generator
from pathlib import Path, PosixPath

import yaml
from jinja2 import Template

git_root_dir = next(iter([x for x in Path(__file__).resolve().parents if (x / ".git").is_dir()]), None)


dirs_to_skip = ["bin", "requirements", "venv"]


def list_docker_dirs() -> Generator[PosixPath]:
    """List all Docker project directories in the git root."""
    yield from [
        _dir
        for _dir in sorted(git_root_dir.iterdir())
        if _dir.is_dir() and _dir.name not in dirs_to_skip and not _dir.name.startswith(".")
    ]


def read_test_config(git_root, docker_image_dirs) -> dict:
    docker_image_config = {}

    for docker_image_dir in docker_image_dirs:
        test_config_path = git_root / docker_image_dir / "test.yaml"

        if not test_config_path.exists():
            print("ERROR: missing file", test_config_path)
            raise SystemExit(1)

        with open(test_config_path) as file:
            config = yaml.safe_load(file)

        if config is not None and "docker" in config:
            docker_config = config["docker"]
            docker_image_config[docker_image_dir] = docker_config
        else:
            docker_image_config[docker_image_dir] = []

    return docker_image_config


def main():
    """Render the Jinja2 template file."""
    docker_compose_template_path = git_root_dir / "docker-compose.yaml.j2"
    docker_compose_path = git_root_dir / "docker-compose.yaml"
    dir_names = [dir.name for dir in list_docker_dirs()]

    template_file_content = docker_compose_template_path.read_text()

    docker_image_dirs = dir_names
    docker_configs = read_test_config(git_root_dir, docker_image_dirs)

    template = Template(template_file_content)
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
