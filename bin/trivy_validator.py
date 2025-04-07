#!/usr/bin/env python3
import json
import os
from pathlib import Path

git_root = [x for x in Path(__file__).resolve().parents if (x / ".git").is_dir()][-1]
project_name = os.getenv("PROJECT_DIRECTORY")
scan_results_file_path = f"{git_root}/{project_name}"

data = json.loads(Path(f"{scan_results_file_path}/scan-results.json").read_text())
found_cves = [vuln["VulnerabilityID"] for result in data.get("Results", []) for vuln in result.get("Vulnerabilities", [])]


def cve_list_to_string(items: list):
    sorted_items = sorted(set(items), key=lambda x: x.lower() if x else "")
    if sorted_items:
        return "\n\n" + "\n".join([f"{item}" for item in sorted_items]) + "\n"
    return "none\n"


def get_ignored_cves() -> list:
    ignore_file = Path(f"{scan_results_file_path}/trivyignore")
    if ignore_file.is_file():
        return sorted({line.strip() for line in ignore_file.read_text().splitlines()})
    return []


ignored_cve_list = get_ignored_cves()

new_cves = [cve for cve in found_cves if cve not in ignored_cve_list]
print(f"New CVEs that are not found in {project_name}/trivyignore: {cve_list_to_string(new_cves)}")

old_cves = [cve for cve in found_cves if cve in ignored_cve_list and cve in found_cves]
print(f"Old CVEs that exist now but are already in {project_name}/trivyignore: {cve_list_to_string(old_cves)}")

solved_cves = [cve for cve in ignored_cve_list if cve not in found_cves]
print(f"Solved CVEs that can be removed from {project_name}/trivyignore: {cve_list_to_string(solved_cves)}")

if new_cves:
    raise SystemExit(1)
