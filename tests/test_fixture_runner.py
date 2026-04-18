"""Run check.sh against pass/ and fail/ fixtures, validate via the contract parser.

This is the canonical pattern for testing every control in agent-weiss:
each control ships with a pass/ fixture (control should report pass) and a
fail/ fixture (control should report fail or setup-unmet). Both stdout and
exit code are validated through parse_check_output, which enforces the
contract (status field present, status matches exit code, valid JSON).
"""
from __future__ import annotations
import subprocess
from pathlib import Path

import pytest

from agent_weiss.lib.contract import Status, parse_check_output

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES = REPO_ROOT / "profiles"
FIXTURES = REPO_ROOT / "fixtures"


def _discover_controls() -> list[Path]:
    """Find every control with both pass/ and fail/ fixtures."""
    discovered: list[Path] = []
    if not FIXTURES.exists():
        return discovered
    for control_dir in FIXTURES.rglob("controls/*"):
        if not control_dir.is_dir():
            continue
        if (control_dir / "pass").is_dir() and (control_dir / "fail").is_dir():
            discovered.append(control_dir)
    return discovered


def _control_check_sh(fixture_control_dir: Path) -> Path:
    """Translate a fixtures path to the corresponding profiles check.sh path.

    Fixture layout mirrors the profiles layout under fixtures/profiles/...,
    so the leading "profiles" component is stripped when mapping to PROFILES.
    """
    relative = fixture_control_dir.relative_to(FIXTURES)
    if relative.parts and relative.parts[0] == "profiles":
        relative = Path(*relative.parts[1:])
    return PROFILES / relative / "check.sh"


@pytest.mark.parametrize("fixture_control_dir", _discover_controls(), ids=lambda p: str(p.relative_to(FIXTURES)))
def test_control_passes_on_pass_fixture(fixture_control_dir: Path):
    """Pass fixture must produce status=pass via the contract parser."""
    check_sh = _control_check_sh(fixture_control_dir)
    assert check_sh.exists(), f"missing check.sh at {check_sh}"

    pass_dir = fixture_control_dir / "pass"
    result = subprocess.run(
        ["sh", str(check_sh)],
        cwd=pass_dir,
        capture_output=True,
        text=True,
    )
    parsed = parse_check_output(stdout=result.stdout, exit_code=result.returncode)
    assert parsed.status is Status.PASS, (
        f"expected status=pass in {pass_dir}, got {parsed.status.value}\n"
        f"summary={parsed.summary!r}"
    )


@pytest.mark.parametrize("fixture_control_dir", _discover_controls(), ids=lambda p: str(p.relative_to(FIXTURES)))
def test_control_fails_on_fail_fixture(fixture_control_dir: Path):
    """Fail fixture must produce status=fail OR status=setup-unmet via the contract parser."""
    check_sh = _control_check_sh(fixture_control_dir)
    assert check_sh.exists(), f"missing check.sh at {check_sh}"

    fail_dir = fixture_control_dir / "fail"
    result = subprocess.run(
        ["sh", str(check_sh)],
        cwd=fail_dir,
        capture_output=True,
        text=True,
    )
    parsed = parse_check_output(stdout=result.stdout, exit_code=result.returncode)
    assert parsed.status in (Status.FAIL, Status.SETUP_UNMET), (
        f"expected status=fail or setup-unmet in {fail_dir}, got {parsed.status.value}\n"
        f"summary={parsed.summary!r}"
    )
