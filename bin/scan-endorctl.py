#!/usr/bin/env python3
"""Scan a Docker image with endorctl and filter findings.

Runs `endorctl container scan` and post-processes the JSON output. A finding
fails the build when ALL of these are true:
  - severity is at or above --severity (default: high)
  - its CVE ID is not in the optional endorignore file
  - a fix version is available for the finding

Findings at or above the severity threshold are always printed, even when no
fix version is available — those are reported as informational and do not fail
the build.

Devs triage findings by adding the CVE ID to the per-image endorignore file
after reviewing it in the Endor UI.

If --path is provided and that directory contains a file named `endorignore`,
each non-blank, non-comment line is treated as a CVE ID to ignore.

If --image-tar is provided, endorctl scans the tarball directly (no local
docker daemon required); --image is still passed so findings are tagged with
the desired image name/tag.

With --debug, the full JSON of every finding at or above the severity threshold
is printed (plus the top-level keys of the scan output), to find out which fields
carry file locations. --raw-out additionally saves the unfiltered endorctl JSON.

Usage:
    uv run scan-endorctl.py --image <name:tag> [--image-tar <path>] [--path <dir>]
        [--severity {critical,high,medium,low}] [--debug] [--raw-out <file>]
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


def _extract_web_url(stderr: str) -> str | None:
    for line in stderr.splitlines():
        match = re.search(r"(https://app\.endorlabs\.com/\S+)", line)
        if match:
            return match.group(1)
    return None


def run_endorctl(image: str, image_tar: Path | None) -> tuple[dict, str | None]:
    """Run endorctl container scan and return parsed JSON + web URL."""
    cmd = ["endorctl", "container", "scan", "--image", image, "-o", "json"]
    if image_tar is not None:
        cmd.append(f"--image-tar={image_tar}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # noqa: S603
    except subprocess.TimeoutExpired:
        print(f"Error: endorctl timed out after 300 seconds scanning {image}", file=sys.stderr)
        sys.exit(2)
    for line in result.stderr.splitlines():
        if "WARNING vulnerability-error: Unable to map severity" in line:
            continue
        print(line, file=sys.stderr)
    stdout = result.stdout
    if not stdout.strip():
        # endorctl uploads container-scan results to the backend and only emits
        # JSON on stdout when there are findings to format. A clean scan (zero
        # findings) exits 0 with empty stdout — that is a pass, not an error.
        if result.returncode == 0:
            print("endorctl produced no JSON output (clean scan, results uploaded to Endor API).")
            return {"all_findings": []}, _extract_web_url(result.stderr)
        print(f"Error: endorctl exited {result.returncode} with no JSON output.", file=sys.stderr)
        sys.exit(2)
    web_url = _extract_web_url(result.stderr)
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


def _vuln_spec(finding: dict) -> dict:
    return finding.get("spec", {}).get("finding_metadata", {}).get("vulnerability", {}).get("spec", {})


def get_aliases(finding: dict) -> list[str]:
    """All IDs this finding is known by (GHSA, CVE, GO-…), from the vuln aliases."""
    return _vuln_spec(finding).get("aliases", [])


def is_vulnerability(finding: dict) -> bool:
    return "FINDING_CATEGORY_VULNERABILITY" in finding.get("spec", {}).get("finding_categories", [])


def get_vuln_id(finding: dict) -> str:
    """Human-facing ID for the finding, preferring the CVE when one exists."""
    cve = next((a for a in get_aliases(finding) if a.startswith("CVE-")), None)
    if cve:
        return cve
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


def get_remediation(finding: dict) -> str:
    """Endor's remediation text, which names the parent dependency that pulls in the vulnerable package.

    Container findings carry no file path; for Go binaries this chain (e.g. "Update
    github.com/foo/bar@v1 to use golang.org/x/net version 0.60.0") is the closest thing to a location.
    """
    spec = finding.get("spec", {})
    return spec.get("remediation") or spec.get("relationship") or ""


def has_fix_version(finding: dict) -> bool:
    proposed = finding.get("spec", {}).get("proposed_version", "")
    return bool(proposed) and proposed != "?"


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


def _leaf_paths(value: object, prefix: str = "") -> list[str]:
    """Dotted paths of every leaf in a JSON value; list items are collapsed to `[]`."""
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in _leaf_paths(v, f"{prefix}.{k}" if prefix else k)]
    if isinstance(value, list):
        return [p for item in value for p in _leaf_paths(item, f"{prefix}[]")] or [f"{prefix}[]"]
    return [prefix]


def print_debug(data: dict, findings: list[dict]) -> None:
    """Dump raw finding JSON so we can see which fields (if any) hold file locations."""
    other_keys = sorted(k for k in data if k != "all_findings")
    print("\n===== DEBUG: top-level keys of endorctl output =====")
    print(f"all_findings: {len(data.get('all_findings', []))} total; other keys: {other_keys}")
    for key in other_keys:
        print(f"--- {key} ---")
        print(json.dumps(data[key], indent=2, sort_keys=True)[:5000])
    print("\n===== DEBUG: unique leaf key paths across displayed findings =====")
    for path in sorted({p for f in findings for p in _leaf_paths(f)}):
        print(path)
    print("\n===== DEBUG: raw findings =====")
    for f in findings:
        print(f"--- {get_vuln_id(f)} {get_severity(f)} {get_package_info(f)[0]} ---")
        print(json.dumps(f, indent=2, sort_keys=True))
    print("===== END DEBUG =====\n")


def _yaml_scalar(value: str) -> str:
    """Render a string as a YAML scalar: plain when that is unambiguous, else double-quoted (JSON strings are valid YAML)."""
    needs_quotes = (
        not value
        or ": " in value
        or " #" in value
        or value != value.strip()
        or not value.isprintable()  # newlines, control chars, U+2028/U+2029: must not split the line
        or value[0] in "-?:,[]{}#&*!|>'\"%@`"
        or value.endswith(":")
    )
    if not needs_quotes:
        try:
            float(value)
            needs_quotes = True  # e.g. "0.5" would otherwise load as a number
        except ValueError:
            pass
    # Default ensure_ascii=True escapes every non-ASCII and control character, so a quoted value stays on one line.
    return json.dumps(value) if needs_quotes else value


def _yaml_field(key: str, value: str, indent: str) -> list[str]:
    """Render `key: value`, using a literal block (`|-`) for multi-line text so newlines stay human-readable.

    A block scalar cannot hold control characters or U+2028/U+2029, and would mis-load text that starts with
    whitespace or has surrounding blank lines, so those fall back to the quoted single-line form.
    """
    lines = value.split("\n")
    block_safe = (
        len(lines) > 1 and all(line.isprintable() for line in lines) and lines[0] == lines[0].lstrip() and lines[0] and lines[-1]
    )
    if not block_safe:
        return [f"{indent}{key}: {_yaml_scalar(value)}"]
    return [f"{indent}{key}: |-", *(f"{indent}  {line}" if line else "" for line in lines)]


def print_remediation(findings: list[dict]) -> None:
    """Print each distinct remediation once, as a YAML list, with the CVEs it resolves.

    Many CVEs share one package upgrade, so findings are grouped by (package, remediation). A YAML list keeps
    every line short except `remediation`, which stays on one line so it can be copied intact, and survives
    CI log viewers that truncate wide tables.
    """
    grouped: dict[tuple[str, str], dict] = {}
    for f in findings:
        if not (remediation := get_remediation(f)):
            continue
        pkg, current, fix = get_package_info(f)
        entry = grouped.setdefault((pkg, remediation), {"current": current, "fix": fix, "cves": []})
        entry["cves"].append(get_vuln_id(f))
    if not grouped:
        return
    print(f"Remediation steps ({len(grouped)} items)")
    for n, ((pkg, remediation), entry) in enumerate(sorted(grouped.items())):
        if n:
            print()
        print(f"- package: {_yaml_scalar(pkg)}")
        print(f"  current: {_yaml_scalar(entry['current'])}")
        print(f"  fix: {_yaml_scalar(entry['fix'])}")
        print("  cves:")
        for cve in sorted(entry["cves"]):
            print(f"    - {_yaml_scalar(cve)}")
        print("\n".join(_yaml_field("remediation", remediation, "  ")))
    print()


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
        "--debug",
        action="store_true",
        help="Print the full JSON of every finding at or above --severity, to discover available fields (e.g. file paths)",
    )
    parser.add_argument(
        "--raw-out",
        type=Path,
        default=None,
        help="Write the unfiltered endorctl JSON output to this file",
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
    if args.raw_out:
        args.raw_out.write_text(json.dumps(data, indent=2, sort_keys=True))
        print(f"Raw endorctl JSON written to {args.raw_out}")

    findings = [f for f in data.get("all_findings", []) if is_vulnerability(f)]
    at_severity = [f for f in findings if severity_at_or_above(f, args.severity)]

    if args.debug:
        print_debug(data, at_severity)

    ignored_cves = load_ignored_cves(args.path)

    actionable: list[dict] = []
    ignored: list[dict] = []
    no_fix: list[dict] = []
    for f in at_severity:
        if ignored_cves.intersection(get_aliases(f)) or get_vuln_id(f) in ignored_cves:
            ignored.append(f)
        elif not has_fix_version(f):
            no_fix.append(f)
        else:
            actionable.append(f)

    print(f"\nGate: fail on severity >= {args.severity} when a fix version is available")
    if actionable:
        print_table(actionable, "Vulnerabilities (action required)")
        print_remediation(actionable)
    if no_fix:
        print_table(no_fix, "Vulnerabilities without a fix version (informational, does not fail build)")
        print_remediation(no_fix)
    if ignored:
        print_table(ignored, f"Ignored vulnerabilities (in {args.path}/endorignore)")
    if not actionable:
        print(f"No actionable vulnerabilities at or above {args.severity}.")

    sys.exit(1 if actionable else 0)


if __name__ == "__main__":
    main()
