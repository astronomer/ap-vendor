#!/usr/bin/env python3
"""This script is used to create the circle config file so that we can stay
DRY."""

from collections.abc import Generator
from pathlib import Path, PosixPath

from jinja2 import Template

git_root_dir = next(iter([x for x in Path(__file__).resolve().parents if (x / ".git").is_dir()]), None)

dirs_to_skip = ["bin", "requirements", "venv"]
required_files = ["Dockerfile", "version.txt", "test.yaml"]


def list_docker_dirs() -> Generator[PosixPath]:
    """List all Docker project directories in the git root."""
    yield from [
        _dir
        for _dir in sorted(git_root_dir.iterdir())
        if _dir.is_dir() and _dir.name not in dirs_to_skip and not _dir.name.startswith(".")
    ]


def ensure_required_files_exist():
    """Make sure required files exist in all Docker directories. Report missing files."""
    errors = []
    for subdir in list_docker_dirs():
        errors.extend(
            f"ERROR: missing file {subdir.name}/{required_file}"
            for required_file in required_files
            if not (subdir / required_file).is_file()
        )
    if errors:
        print("\n".join(errors))
        print("\nAny directory that is not a docker build directory must be added to bin/generate_circleci_config.py dirs_to_skip.")
        print("\nAll docker build directories must have the following files:")
        for file in required_files:
            print(f"  - {file}")
        print("\nOptional files are:")
        print("  - trivyignore")
        print("  - trivy.yaml")
        exit(1)


def main():
    """Render the Jinja2 template file."""
    ensure_required_files_exist()

    circle_directory = git_root_dir / ".circleci"
    config_template_path = circle_directory / "config.yml.j2"
    config_path = circle_directory / "config.yml"
    dir_names = [dir.name for dir in list_docker_dirs()]

    with config_template_path.open() as circle_ci_config_template:
        templated_file_content = circle_ci_config_template.read()
    template = Template(templated_file_content)
    config = template.render(directories=dir_names)
    warning_header = (
        "# Warning: automatically generated file\n"
        + "# Please edit .circleci/config.yml.j2, then run bin/generate_circleci_config.py\n"
    )
    with config_path.open("w") as circle_ci_config_file:
        circle_ci_config_file.write(warning_header)
        circle_ci_config_file.write(config + "\n")

    # Continue Config
    continue_config_template_path = circle_directory / "continue-config.yml.j2"
    continue_config_path = circle_directory / "continue-config.yml"

    with continue_config_template_path.open() as continue_circle_ci_config_template:
        templated_file_content = continue_circle_ci_config_template.read()
    continue_template = Template(templated_file_content)
    continue_config = continue_template.render(
        directories=dir_names,
        workflow_directories=dir_names,
    )

    continue_warning_header = (
        "# Warning: automatically generated file\n"
        + "# Please edit .circleci/continue_config.yml.j2, then run bin/generate_circleci_config.py\n"
    )

    with continue_config_path.open("w") as continue_circle_ci_config_file:
        continue_circle_ci_config_file.write(continue_warning_header)
        continue_circle_ci_config_file.write(continue_config + "\n")


if __name__ == "__main__":
    main()
