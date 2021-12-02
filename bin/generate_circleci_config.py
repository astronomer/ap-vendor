#!/usr/bin/env python3
"""
This script is used to create the circle config file so that we can stay DRY.
"""
from pathlib import Path

from jinja2 import Template

dirs_to_skip = ["bin"]
required_files = ["Dockerfile", "version.txt"]


def list_docker_dirs(path):
    dirs = [
        _dir
        for _dir in sorted(path.iterdir())
        if _dir.is_dir()
        and _dir.name not in dirs_to_skip
        and not _dir.name.startswith(".")
    ]
    for subdir in dirs:
        for required_file in required_files:
            if not Path(subdir / required_file).is_file():
                raise Exception(
                    f"ERROR: you must put a file '{required_file}' in {subdir}\n"
                    + "If this is is not intended to be a Docker image, then make it a hidden directory or add it to dirs_to_skip"
                )
        yield subdir.name


def main():
    """Render the Jinja2 template file"""
    circle_directory = Path(__file__).parent.parent / ".circleci"
    config_template_path = circle_directory / "config.yml.j2"
    config_path = circle_directory / "config.yml"

    with config_template_path.open() as circle_ci_config_template:
        templated_file_content = circle_ci_config_template.read()
    template = Template(templated_file_content)
    config = template.render(directories=list_docker_dirs(circle_directory.parent))
    warning_header = (
        "# Warning: automatically generated file\n"
        + "# Please edit .circleci/config.yml.j2, then run bin/generate_circleci_config.py\n"
    )
    with config_path.open("w") as circle_ci_config_file:
        circle_ci_config_file.write(warning_header)
        circle_ci_config_file.write(config)


if __name__ == "__main__":
    main()
