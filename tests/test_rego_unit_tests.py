"""Self-test: every policy.rego has a policy_test.rego and the unit tests pass."""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES = REPO_ROOT / "profiles"


def _all_policies() -> list[Path]:
    return sorted(PROFILES.rglob("policy.rego"))


@pytest.mark.parametrize("policy", _all_policies(), ids=lambda p: str(p.relative_to(PROFILES)))
def test_policy_has_test_sibling(policy: Path):
    """Every policy.rego must ship a policy_test.rego sibling."""
    sibling = policy.with_name("policy_test.rego")
    assert sibling.exists(), f"missing {sibling}"


@pytest.mark.skipif(shutil.which("conftest") is None, reason="conftest not installed")
@pytest.mark.parametrize("policy", _all_policies(), ids=lambda p: str(p.relative_to(PROFILES)))
def test_policy_unit_tests_pass(policy: Path):
    """conftest verify must succeed for every policy.rego (and its _test sibling)."""
    sibling = policy.with_name("policy_test.rego")
    if not sibling.exists():
        pytest.skip("no test sibling")
    proc = subprocess.run(
        ["conftest", "verify", "--policy", str(policy.parent)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"conftest verify failed for {policy.relative_to(PROFILES)}\n"
        f"stdout: {proc.stdout}\n"
        f"stderr: {proc.stderr}"
    )
