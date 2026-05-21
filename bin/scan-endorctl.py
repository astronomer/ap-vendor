#!/usr/bin/env python3
"""Scan a Docker image with endorctl and filter findings.

Runs `endorctl container scan` and post-processes the JSON output. A finding
fails the build when BOTH of these are true:
  - severity is at or above --severity (default: high)
  - its CVE ID is not in the optional endorignore file

Devs triage findings by adding the CVE ID to the per-image endorignore file
after reviewing it in the Endor UI.

If --path is provided and that directory contains a file named `endorignore`,
each non-blank, non-comment line is treated as a CVE ID to ignore.

If --image-tar is provided, endorctl scans the tarball directly (no local
docker daemon required); --image is still passed so findings are tagged with
the desired image name/tag.

Usage:
    uv run scan-endorctl.py --image <name:tag> [--image-tar <path>] [--path <dir>] [--severity {critical,high,medium,low}]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from tabulate import tabulate

_GIT_HASH_RE = re.compile(r"[0-9a-f]{40}")


def _is_git_hash(value: str) -> bool:
    return bool(_GIT_HASH_RE.fullmatch(value))


def run_endorctl(image: str, image_tar: Path | None) -> tuple[dict, str | None]:
    """Run endorctl container scan and return parsed JSON + web URL."""
    cmd = ["endorctl", "container", "scan", "--image", image, "-o", "json"]
    if image_tar is not None:
        cmd.append(f"--image-tar={image_tar}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print(f"Error: endorctl timed out after 300 seconds scanning {image}", file=sys.stderr)
        sys.exit(2)
    print(result.stderr, file=sys.stderr, end="")
    stdout = result.stdout
    if not stdout.strip():
        print("Error: endorctl produced no JSON output.", file=sys.stderr)
        sys.exit(2)
    web_url = None
    for line in result.stderr.splitlines():
        match = re.search(r"(https://app\.endorlabs\.com/\S+)", line)
        if match:
            web_url = match.group(1)
    try:
        return json.loads(stdout), web_url
    except json.JSONDecodeError as e:
        print(f"Error: endorctl produced invalid JSON: {e}", file=sys.stderr)
        print(f"First 500 chars of stdout: {stdout[:500]}", file=sys.stderr)
        sys.exit(2)


def load_ignored_cves(path: Path | None) -> set[str]:
    if path is None:
        return set()
    ignore_file = path / "endorignore"
    try:
        text = ignore_file.read_text()
    except FileNotFoundError:
        return set()
    cves: set[str] = set()
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            cves.add(line)
    return cves


def get_vuln_id(finding: dict) -> str:
    return finding.get("spec", {}).get("extra_key", "") or finding.get("meta", {}).get("name", "unknown")


def get_severity(finding: dict) -> str:
    level = finding.get("spec", {}).get("level", "")
    return level.removeprefix("FINDING_LEVEL_").capitalize()


def get_package_info(finding: dict) -> tuple[str, str, str]:
    spec = finding.get("spec", {})
    pkg_name = spec.get("target_dependency_name", "?")
    current_ver = spec.get("target_dependency_version", "?")
    proposed = spec.get("proposed_version", "?")
    if _is_git_hash(proposed):
        fix_ver = proposed[:12] + " (commit)"
    else:
        fix_ver = proposed
    return pkg_name, current_ver, fix_ver


def get_description(finding: dict) -> str:
    return finding.get("meta", {}).get("description", "")


_SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
_SEVERITY_CHOICES = ["critical", "high", "medium", "low"]


def severity_at_or_above(finding: dict, threshold: str) -> bool:
    """True iff finding's severity is at or above the threshold."""
    finding_sev = get_severity(finding)
    finding_rank = _SEVERITY_ORDER.get(finding_sev)
    if finding_rank is None:
        return False
    threshold_rank = _SEVERITY_ORDER[threshold.capitalize()]
    return finding_rank <= threshold_rank


def print_table(findings: list[dict], title: str) -> None:
    if not findings:
        return
    rows = []
    for f in findings:
        severity = get_severity(f)
        pkg, current, fix = get_package_info(f)
        desc = get_description(f)
        if len(desc) > 80:
            desc = desc[:77] + "..."
        rows.append((_SEVERITY_ORDER.get(severity, 99), get_vuln_id(f), severity, pkg, current, fix, desc))
    rows.sort()
    headers = ["CVE ID", "Severity", "Package", "Version", "Fix Version", "Description"]
    print(f"\n{title} ({len(findings)} findings)")
    print(tabulate([r[1:] for r in rows], headers=headers, tablefmt="simple"))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan a Docker image with endorctl and filter findings.")
    parser.add_argument("--image", required=True, help="Image name:tag to associate with findings")
    parser.add_argument(
        "--image-tar",
        type=Path,
        default=None,
        help="Path to a Docker image tarball. When set, endorctl scans the tar directly (no daemon needed).",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Directory containing an optional `endorignore` file (one CVE ID per line, # comments allowed)",
    )
    parser.add_argument(
        "--severity",
        choices=_SEVERITY_CHOICES,
        default="high",
        help="Minimum severity that fails the build (default: high)",
    )
    parser.add_argument(
        "--debug-json",
        action="store_true",
        help="Dump the full raw JSON returned by endorctl, then exit 0 (no gating).",
    )
    args = parser.parse_args()

    print(f"Scanning image: {args.image}")
    repro = f"endorctl container scan --image={args.image}"
    if args.image_tar:
        repro += f" --image-tar={args.image_tar}"
    print(f"Scan yourself with: {repro}")
    data, web_url = run_endorctl(args.image, args.image_tar)

    if web_url:
        print(f"Full results: {web_url}")

    if args.debug_json:
        print("\n===== BEGIN RAW endorctl JSON =====")
        print(json.dumps(data, indent=2, sort_keys=True))
        print("===== END RAW endorctl JSON =====")
        print(f"Top-level keys: {sorted(data.keys())}")
        sys.exit(0)

    findings = data.get("findings", [])
    at_severity = [f for f in findings if severity_at_or_above(f, args.severity)]

    ignored_cves = load_ignored_cves(args.path)

    actionable: list[dict] = []
    ignored: list[dict] = []
    for f in at_severity:
        (ignored if get_vuln_id(f) in ignored_cves else actionable).append(f)

    print(f"\nGate: fail on severity >= {args.severity}")
    if actionable:
        print_table(actionable, "Vulnerabilities (action required)")
    if ignored:
        print_table(ignored, f"Ignored vulnerabilities (in {args.path}/endorignore)")
    if not actionable:
        print(f"No vulnerabilities at or above {args.severity}.")

    sys.exit(1 if actionable else 0)


if __name__ == "__main__":
    main()
