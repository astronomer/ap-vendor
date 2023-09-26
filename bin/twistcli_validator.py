import json
import sys
import os
from pathlib import Path


ROOT_DIRECTORY = Path(__file__).parent.parent
PROJECT_NAME = os.getenv("PROJECT_DIRECTORY")
SCAN_RESULTS_FILE_PATH = f"{ROOT_DIRECTORY}/{PROJECT_NAME}"
output = []

with open(f"{SCAN_RESULTS_FILE_PATH}/scan-results.json", "r") as f:
    data = json.load(f)
    vulnerabilities = data.get("results", [])[0].get("vulnerabilities", [])
    output = [vul["id"] for vul in vulnerabilities]

try:
    with open(f"{SCAN_RESULTS_FILE_PATH}/twistcliignore", "r") as f:
        ignore_list = [line.strip() for line in f.read().splitlines()]
        if ignore_list == output:
            print("vuln is in ignore list")
        else:
            print("New vulnerabilities found.Fix them or add into ignore list")
            sys.exit(1)
except FileNotFoundError:
    if len(output) > 0:
       print("New vulnerabilities found.Fix them or add into ignore list")
       sys.exit(1)
