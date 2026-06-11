#!/usr/bin/env python3
"""
Analyze GitHub security alerts and generate remediation plan.
Usage: ./fetch.sh owner/repo | python analyze.py
"""

import sys
import json


def summarize_code_scanning(alerts):
    """Summarize code scanning alerts by severity and rule."""
    if not alerts:
        return None

    by_severity = {}
    by_rule = {}

    for alert in alerts:
        rule = alert.get("rule", {})
        severity = rule.get("severity", "unknown")
        rule_id = rule.get("id", "unknown")
        rule_desc = rule.get("description", "No description")

        by_severity[severity] = by_severity.get(severity, 0) + 1

        if rule_id not in by_rule:
            by_rule[rule_id] = {
                "description": rule_desc,
                "severity": severity,
                "count": 0,
                "locations": []
            }
        by_rule[rule_id]["count"] += 1

        # Capture up to 5 example locations
        if len(by_rule[rule_id]["locations"]) < 5:
            instance = alert.get("most_recent_instance", {})
            location = instance.get("location", {})
            by_rule[rule_id]["locations"].append({
                "file": location.get("path", "unknown"),
                "line": location.get("start_line", "?"),
                "message": instance.get("message", {}).get("text", "")[:200]
            })

    return {
        "total": len(alerts),
        "by_severity": by_severity,
        "by_rule": by_rule
    }


def summarize_dependabot(alerts):
    """Summarize dependabot alerts by severity and package."""
    if not alerts:
        return None

    by_severity = {}
    by_package = {}

    for alert in alerts:
        vuln = alert.get("security_vulnerability", {})
        advisory = alert.get("security_advisory", {})
        dep = alert.get("dependency", {})
        pkg = dep.get("package", {})

        severity = vuln.get("severity", "unknown")
        pkg_name = pkg.get("name", "unknown")
        ecosystem = pkg.get("ecosystem", "unknown")

        by_severity[severity] = by_severity.get(severity, 0) + 1

        if pkg_name not in by_package:
            by_package[pkg_name] = {
                "ecosystem": ecosystem,
                "count": 0,
                "max_severity": severity,
                "vulnerabilities": []
            }
        by_package[pkg_name]["count"] += 1

        # Track highest severity
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        if severity_order.get(severity, 0) > severity_order.get(by_package[pkg_name]["max_severity"], 0):
            by_package[pkg_name]["max_severity"] = severity

        # Capture vulnerability details (up to 5 per package)
        if len(by_package[pkg_name]["vulnerabilities"]) < 5:
            patched = vuln.get("first_patched_version", {})
            by_package[pkg_name]["vulnerabilities"].append({
                "ghsa_id": advisory.get("ghsa_id", ""),
                "cve_id": advisory.get("cve_id", ""),
                "summary": advisory.get("summary", "")[:200],
                "vulnerable_range": vuln.get("vulnerable_version_range", ""),
                "patched_version": patched.get("identifier") if patched else "No patch available"
            })

    return {
        "total": len(alerts),
        "by_severity": by_severity,
        "by_package": by_package
    }


def summarize_secret_scanning(alerts):
    """Summarize secret scanning alerts by secret type."""
    if not alerts:
        return None

    by_type = {}

    for alert in alerts:
        secret_type = alert.get("secret_type_display_name") or alert.get("secret_type", "unknown")

        if secret_type not in by_type:
            by_type[secret_type] = {
                "count": 0,
                "alerts": []
            }
        by_type[secret_type]["count"] += 1

        # Capture alert details (up to 5 per type)
        if len(by_type[secret_type]["alerts"]) < 5:
            by_type[secret_type]["alerts"].append({
                "number": alert.get("number"),
                "created_at": alert.get("created_at", ""),
                "state": alert.get("state", ""),
                "secret_type": alert.get("secret_type", ""),
                "push_protection_bypassed": alert.get("push_protection_bypassed", False)
            })

    return {
        "total": len(alerts),
        "by_type": by_type
    }


def generate_report(data):
    """Generate markdown remediation report."""
    repo = data["repository"]
    code = data.get("code_scanning_summary")
    deps = data.get("dependabot_summary")
    secrets = data.get("secret_scanning_summary")

    lines = [
        f"# Security Remediation Plan: {repo}",
        "",
        "## Summary",
        "",
        "| Category | Critical | High | Medium | Low | Total |",
        "|----------|----------|------|--------|-----|-------|",
    ]

    # Code scanning row
    if code:
        sev = code["by_severity"]
        lines.append(f"| Code Scanning | {sev.get('critical', 0)} | {sev.get('high', 0)} | {sev.get('medium', 0)} | {sev.get('low', 0)} | {code['total']} |")
    else:
        lines.append("| Code Scanning | - | - | - | - | 0 |")

    # Dependabot row
    if deps:
        sev = deps["by_severity"]
        lines.append(f"| Dependabot | {sev.get('critical', 0)} | {sev.get('high', 0)} | {sev.get('medium', 0)} | {sev.get('low', 0)} | {deps['total']} |")
    else:
        lines.append("| Dependabot | - | - | - | - | 0 |")

    # Secret scanning row
    if secrets:
        lines.append(f"| Secret Scanning | - | - | - | - | {secrets['total']} |")
    else:
        lines.append("| Secret Scanning | - | - | - | - | 0 |")

    # Code Scanning Details
    if code and code["by_rule"]:
        lines.extend(["", "---", "", "## Code Scanning Fixes", ""])
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}
        sorted_rules = sorted(code["by_rule"].items(), key=lambda x: severity_order.get(x[1]["severity"], 99))
        
        for rule_id, info in sorted_rules:
            lines.extend([
                f"### `{rule_id}`",
                f"**{info['description']}**",
                "",
                f"**Severity:** {info['severity']} | **Count:** {info['count']}",
                "",
                "**Affected locations:**",
            ])
            for loc in info["locations"]:
                lines.append(f"- `{loc['file']}:{loc['line']}` - {loc['message'][:100]}")
            lines.append("")

    # Dependabot Details
    if deps and deps["by_package"]:
        lines.extend(["", "---", "", "## Dependabot Fixes", ""])
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}
        sorted_packages = sorted(deps["by_package"].items(), key=lambda x: severity_order.get(x[1]["max_severity"], 99))
        
        for pkg_name, info in sorted_packages:
            lines.extend([
                f"### {pkg_name} ({info['ecosystem']})",
                f"**Severity:** {info['max_severity']} | **Vulnerabilities:** {info['count']}",
                "",
            ])
            for vuln in info["vulnerabilities"]:
                advisory_id = vuln["ghsa_id"] or vuln["cve_id"] or "N/A"
                lines.extend([
                    f"- **{advisory_id}**: {vuln['summary']}",
                    f"  - Vulnerable: `{vuln['vulnerable_range']}`",
                    f"  - Fix: `{vuln['patched_version']}`",
                ])
            
            # Add upgrade command hint based on ecosystem
            ecosystem = info["ecosystem"].lower()
            if ecosystem == "npm":
                lines.append(f"\n```bash\nnpm update {pkg_name}\n# or for major version: npm install {pkg_name}@latest\n```")
            elif ecosystem == "pip":
                lines.append(f"\n```bash\npip install --upgrade {pkg_name}\n```")
            elif ecosystem == "go":
                lines.append(f"\n```bash\ngo get -u {pkg_name}\n```")
            elif ecosystem == "rubygems":
                lines.append(f"\n```bash\nbundle update {pkg_name}\n```")
            elif ecosystem == "nuget":
                lines.append(f"\n```bash\ndotnet add package {pkg_name}\n```")
            elif ecosystem == "maven":
                lines.append(f"\n*Update version in pom.xml*")
            lines.append("")

    # Secret Scanning Details
    if secrets and secrets["by_type"]:
        lines.extend(["", "---", "", "## Secret Scanning Remediation", ""])
        
        for secret_type, info in secrets["by_type"].items():
            lines.extend([
                f"### {secret_type}",
                f"**Found:** {info['count']} instance(s)",
                "",
                "**Immediate actions:**",
                "1. **Rotate the secret immediately** - Generate a new credential",
                "2. **Revoke the exposed secret** - Invalidate the old credential",
                "3. **Check git history** - Secret may exist in previous commits",
                "4. **Update references** - Update environment variables / secrets manager",
                "",
                "**Prevention:**",
                "- Use environment variables or a secrets manager",
                "- Add patterns to `.gitignore`",
                "- Enable push protection in GitHub settings",
                "- Use pre-commit hooks to scan for secrets",
                "",
            ])

    # No issues found
    total = (code["total"] if code else 0) + (deps["total"] if deps else 0) + (secrets["total"] if secrets else 0)
    if total == 0:
        lines.extend([
            "",
            "## ✅ No Open Security Alerts",
            "",
            "This repository has no open security alerts. Great job!",
        ])

    return "\n".join(lines)


def main():
    # Read JSON from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate summaries
    data["code_scanning_summary"] = summarize_code_scanning(data.get("code_scanning", []))
    data["dependabot_summary"] = summarize_dependabot(data.get("dependabot", []))
    data["secret_scanning_summary"] = summarize_secret_scanning(data.get("secret_scanning", []))

    # Output mode: --json for raw data, otherwise markdown report
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(data, indent=2))
    else:
        print(generate_report(data))


if __name__ == "__main__":
    main()
