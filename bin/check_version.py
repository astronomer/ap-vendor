#!/usr/bin/env python3
"""Verify that a given ap-vendor component directory has a valid semver in its version.txt file, and print it out."""
import sys

from packaging.version import parse as semver

try:
    directory = sys.argv[1]
except IndexError:
    print("ERROR: no directory given.\n")
    print(f"Description: {__doc__}\n")
    print(f"Usage:       {sys.argv[0]} <dir_to_check>")
    sys.exit(1)

try:
    with open(f"{ directory }/version.txt") as version_file:
        version = version_file.read().strip()
except FileNotFoundError:
    print(f"ERROR: version.txt not found in {directory}")
    sys.exit(1)

if not semver(version).release:
    sys.stderr.write(f"Please provide a semantic version in { directory }/version.txt")
    exit(1)

sys.stdout.write(version)
