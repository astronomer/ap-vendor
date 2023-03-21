#!/usr/bin/env python3
"""This script is used to create the docker-compose file so that we can stay
DRY."""
from pathlib import Path

import yaml
from jinja2 import Template

dirs_to_skip = [
    ".circleci",
    ".git",
    ".github",
    ".idea",
    ".pytest_cache",
    ".ruff_cache",
    "bin",
    "requirements",
    "venv",
]


def list_docker_dirs(path) -> list[str]:
    """Return a list of docker image directories."""
    return sorted(
        [
            x.stem
            for x in Path(path).glob("*")
            if x.is_dir() and x.name not in dirs_to_skip
        ]
    )


def read_test_config(git_root, docker_image_dirs) -> dict:
    docker_image_config = {}

    for docker_image_dir in docker_image_dirs:
        test_config_path = git_root / docker_image_dir / "test.yaml"

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
    git_root = Path(__file__).parent.parent
    docker_compose_template_path = git_root / "docker-compose.yaml.j2"
    docker_compose_path = git_root / "docker-compose.yaml"

    template_file_content = docker_compose_template_path.read_text()

    docker_image_dirs = list_docker_dirs(git_root)
    docker_configs = read_test_config(git_root, docker_image_dirs)

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
