#!/usr/bin/env python3
import json
from pathlib import Path
import os


git_root = [x for x in Path(__file__).resolve().parents if (x / ".git").is_dir()][-1]
project_name = os.getenv("PROJECT_DIRECTORY")
scan_results_file_path = f"{git_root}/{project_name}"

data = json.loads(Path(f"{scan_results_file_path}/scan-results.json").read_text())
found_cves = [
    vuln["id"] for vuln in data.get("results", [])[0].get("vulnerabilities", [])
]


def cve_list_to_string(list):
    if list:
        return "\n" + "\n".join([f"  - {item}" for item in list if item]) + "\n"
    return "none\n"


def get_ignored_cves():
    ignore_file = Path(f"{scan_results_file_path}/twistcliignore")
    if ignore_file.is_file():
        return [line.strip() for line in ignore_file.read_text().splitlines()]
    return []


ignored_cve_list = get_ignored_cves()

if found_cves:
    print(
        f"New vulnerabilities found. Fix them or add them to {project_name}/twistcliignore\n"
    )

    new_cves = [cve for cve in found_cves if cve not in ignored_cve_list]
    print(
        f"New CVEs that are not found in {project_name}/twistcliignore: {cve_list_to_string(new_cves)}"
    )

old_cves = [cve for cve in found_cves if cve in ignored_cve_list and cve in found_cves]
print(
    f"Old CVEs that exist now but are already in {project_name}/twistcliignore: {cve_list_to_string(old_cves)}"
)

solved_cves = [cve for cve in ignored_cve_list if cve not in found_cves]
print(
    f"Solved CVEs that can be removed from {project_name}/twistcliignore: {cve_list_to_string(solved_cves)}"
)


if found_cves:
    raise SystemExit(1)
