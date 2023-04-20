#!/usr/bin/env python3

import sys

from packaging.version import parse as semver, InvalidVersion
from pathlib import Path

errors = 0

for file in sys.argv[1:]:
    version = Path(file).read_text().strip()

    try:
        semver(version)
        print(f"OK {file} {version}")
    except InvalidVersion:
        print(f"ERROR {file} {version}")
        errors = errors + 1


raise SystemExit(errors)
