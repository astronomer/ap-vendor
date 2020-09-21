#!/usr/bin/env python3
"""
This script is used to create the circle config file
so that we can stay DRY.
"""

import os
from jinja2 import Template

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            subdir = os.path.join(path, f)
            for required_file in ["Dockerfile", "version.txt", "cve-whitelist.yaml"]:
                if not required_file in os.listdir(subdir):
                    raise Exception(f"ERROR: you must put a file '{ required_file }' in { subdir }\n" +
                                    "If this is is not intended to be a Docker image, then make it a hidden directory")
            yield f

def main():
    """ Render the Jinja2 template file
    """
    circle_directory = os.path.dirname(os.path.realpath(__file__))
    config_template_path = os.path.join(circle_directory, "config.yml.j2")
    config_path = os.path.join(circle_directory, "config.yml")

    with open(config_template_path, "r") as circle_ci_config_template:
        templated_file_content = circle_ci_config_template.read()
    template = Template(templated_file_content)
    config = template.render(
        directories=list(listdir_nohidden(os.path.join(circle_directory,'..')))
    )
    warning_header = "# Warning: automatically generated file\n" + \
                     "# Please edit config.yml.j2, and use the script generate_circleci_config.py\n"
    with open(config_path, "w") as circle_ci_config_file:
        circle_ci_config_file.write(warning_header)
        circle_ci_config_file.write(config)


if __name__ == "__main__":
    main()
