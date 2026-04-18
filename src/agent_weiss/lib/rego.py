"""Shared Rego runner — invoke conftest, parse JSON output, emit agent-weiss contract.

Each Rego-based control's check.sh delegates here via scripts/run_rego_check.sh.
This avoids 10+ controls duplicating the shell parsing logic.
"""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path
from typing import TypedDict


class RegoResult(TypedDict, total=False):
    status: str  # "pass" | "fail" | "setup-unmet"
    findings_count: int
    summary: str
    install: str
    details_path: str


_INSTALL_HINT = (
    "Install conftest: brew install conftest (macOS) or "
    "see https://www.conftest.dev/install/"
)


def run_rego_check(
    target: Path,
    policy: Path,
    data: dict | None = None,
) -> RegoResult:
    """Run conftest against target with given policy. Return contract-shaped dict.

    Behavior:
    - target missing → status=pass with "not present" summary (control N/A)
    - conftest missing → status=setup-unmet with install hint
    - conftest fails to start → status=setup-unmet with stderr summary
    - conftest exits 0 → status=pass, findings_count=0
    - conftest reports failures → status=fail with count + first few messages
    """
    if not target.exists():
        return {
            "status": "pass",
            "findings_count": 0,
            "summary": f"{target.name} not present — control not applicable",
        }

    if shutil.which("conftest") is None:
        return {
            "status": "setup-unmet",
            "summary": "conftest binary not found on PATH",
            "install": _INSTALL_HINT,
        }

    cmd = [
        "conftest", "test",
        str(target),
        "--policy", str(policy),
        "--no-color",
        "--all-namespaces",
        "--output", "json",
    ]
    data_path: Path | None = None
    if data is not None:
        data_path = target.parent / ".agent-weiss-rego-data.json"
        data_path.write_text(json.dumps(data))
        cmd.extend(["--data", str(data_path)])

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return {
            "status": "setup-unmet",
            "summary": "conftest binary not found on PATH",
            "install": _INSTALL_HINT,
        }
    finally:
        if data_path is not None and data_path.exists():
            data_path.unlink()

    return _parse_conftest_output(proc.stdout, proc.returncode)


def _parse_conftest_output(stdout: str, returncode: int) -> RegoResult:
    """Parse conftest's JSON output. Return contract-shaped dict."""
    try:
        records = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        return {
            "status": "setup-unmet",
            "summary": f"conftest produced unparseable output (exit {returncode})",
            "install": _INSTALL_HINT,
        }

    failures: list[str] = []
    for record in records:
        for failure in record.get("failures") or []:
            msg = failure.get("msg", "<no msg>")
            failures.append(msg)

    if not failures:
        return {
            "status": "pass",
            "findings_count": 0,
            "summary": "all policy checks passed",
        }

    preview = "; ".join(failures[:3])
    if len(failures) > 3:
        preview += f"; and {len(failures) - 3} more"
    return {
        "status": "fail",
        "findings_count": len(failures),
        "summary": preview,
    }
