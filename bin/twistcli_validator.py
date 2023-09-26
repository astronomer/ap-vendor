#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path


ROOT_DIRECTORY = [x for x in Path(__file__).resolve().parents if (x / ".git").is_dir()][-1]
PROJECT_NAME = os.getenv("PROJECT_DIRECTORY")
SCAN_RESULTS_FILE_PATH = f"{ROOT_DIRECTORY}/{PROJECT_NAME}"
output = []

data = json.loads(Path(f"{SCAN_RESULTS_FILE_PATH}/scan-results.json").read_text())
output = [vuln["id"] for vuln in data.get("results", [])[0].get("vulnerabilities", [])]

try:
    with open(f"{SCAN_RESULTS_FILE_PATH}/twistcliignore", "r") as f:
        ignore_list = [line.strip() for line in f.read().splitlines()]
        if ignore_list == output:
            print("vuln is in ignore list")
        else:
            print("New vulnerabilities found.Fix them or add into ignore list")
            sys.exit(1)
except FileNotFoundError:
    pass
