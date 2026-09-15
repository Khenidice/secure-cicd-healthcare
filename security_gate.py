"""Security Gate - enforces a severity threshold on the Bandit SAST report.

The gate exits non-zero (failing the pipeline) if any finding at or above
SEVERITY_THRESHOLD is present. This ensures high-severity vulnerabilities
never progress beyond the SAST stage in the CI/CD pipeline.
"""
import json
import sys

SEVERITY_THRESHOLD = "HIGH"  # gate blocks HIGH and CRITICAL findings
SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def main(report_path):
    with open(report_path) as fp:
        data = json.load(fp)

    findings = data.get("results", [])
    blocked = [
        f for f in findings
        if SEVERITY_ORDER.get(f.get("issue_severity", "LOW"), 0)
        >= SEVERITY_ORDER[SEVERITY_THRESHOLD]
    ]

    print(f"Total findings: {len(findings)} | Blocked: {len(blocked)}")
    if blocked:
        print("SECURITY GATE FAILED - high/critical vulnerabilities found:")
        for b in blocked:
            loc = b.get("location", {})
            print(
                f"  - {b.get('test_id')} [{b.get('issue_severity')}] "
                f"-> {loc.get('filename')}:{loc.get('line')} "
                f"({b.get('issue_text', '')[:60]})"
            )
        return 1

    print("SECURITY GATE PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
