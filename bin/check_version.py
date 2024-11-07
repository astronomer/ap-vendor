#!/usr/bin/env python3
"""Verify that a given ap-vendor component directory has a valid semver in its
version.txt file, and print it out."""

import sys
from pathlib import Path

from packaging.version import parse as semver


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def print_usage():
    eprint(f"Description: {__doc__}\n")
    eprint(f"Usage:       {sys.argv[0]} <dir_to_check>\n")


if len(sys.argv) != 2:
    print_usage()
    sys.exit(1)

directory = Path(sys.argv[1]).absolute()

try:
    with open(directory / "version.txt") as version_file:
        version = version_file.read().strip()
except FileNotFoundError:
    eprint(f"ERROR: version.txt not found in {directory}")
    sys.exit(1)

if not semver(version).release:
    eprint(f"ERROR: No valid semver found in {directory}/version.txt")
    sys.exit(1)

print(version)
