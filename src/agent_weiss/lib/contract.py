"""Parse check.sh output per the agent-weiss output contract.

Every check.sh emits exactly one JSON line on stdout (the last JSON line wins
if other lines precede it) and exits 0 / 1 / 127.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    PASS = "pass"
    FAIL = "fail"
    SETUP_UNMET = "setup-unmet"


_STATUS_TO_EXIT = {
    Status.PASS: 0,
    Status.FAIL: 1,
    Status.SETUP_UNMET: 127,
}


class ContractError(ValueError):
    """check.sh output violates the agent-weiss contract."""


@dataclass(frozen=True)
class CheckResult:
    status: Status
    summary: str
    findings_count: int = 0
    install: str | None = None
    details_path: str | None = None


def parse_check_output(stdout: str, exit_code: int) -> CheckResult:
    """Parse a check.sh invocation's stdout + exit code into a CheckResult.

    Behavior:
    - The contract line is the LAST line of stdout that parses as JSON.
    - exit_code MUST match the JSON status (0=pass, 1=fail, 127=setup-unmet).
    - Mismatch or invalid JSON raises ContractError.
    """
    json_obj = _last_json_line(stdout)

    raw_status = json_obj.get("status")
    try:
        status = Status(raw_status)
    except ValueError as e:
        raise ContractError(f"unknown status: {raw_status!r}") from e

    expected_exit = _STATUS_TO_EXIT[status]
    if exit_code != expected_exit:
        raise ContractError(
            f"exit code {exit_code} does not match status {status.value} "
            f"(expected {expected_exit})"
        )

    return CheckResult(
        status=status,
        summary=str(json_obj.get("summary", "")),
        findings_count=int(json_obj.get("findings_count", 0)),
        install=json_obj.get("install"),
        details_path=json_obj.get("details_path"),
    )


def _last_json_line(stdout: str) -> dict:
    """Return the last line of stdout that parses as a JSON object."""
    last: dict | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                last = obj
        except json.JSONDecodeError:
            continue
    if last is None:
        raise ContractError("no JSON contract line found in stdout")
    return last
