#!/usr/bin/env python3
"""Validate semantic version format.

This script can validate semver either from files or from direct string arguments.
Multiple files and version strings are supported.
"""

import argparse
import sys
from pathlib import Path

# semver has strict semver compliance, whereas packaging.version has python nuances
from semver import Version as SemVer


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def validate_version_string(version_string, source="input"):
    """Validate a version string and return True if valid, False otherwise."""
    try:
        SemVer.parse(version_string)
        print(f"OK {source} {version_string}")
        return True
    except ValueError as e:
        print(f"ERROR {source} {version_string}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--files", nargs="*", type=Path, help="File(s) to read version from")
    parser.add_argument("versions", nargs="*", help="Version string(s) to validate")
    args = parser.parse_args()

    # Validate arguments
    if not args.files and not args.versions:
        eprint("ERROR: Must provide either --files argument(s) or version string(s)")
        parser.print_help()
        sys.exit(1)

    errors = 0

    # Process files if provided
    if args.files:
        for file_path in args.files:
            try:
                version_string = file_path.read_text().strip()
                source = str(file_path)
                if not validate_version_string(version_string, source):
                    errors += 1
            except FileNotFoundError:
                eprint(f"ERROR: File not found: {file_path}")
                errors += 1
            except Exception as e:  # noqa: BLE001
                eprint(f"ERROR: Could not read file {file_path}: {e}")
                errors += 1

    # Process version strings if provided
    if args.versions:
        for version_string in args.versions:
            if not validate_version_string(version_string, "argument"):
                errors += 1

    sys.exit(errors)


if __name__ == "__main__":
    main()
