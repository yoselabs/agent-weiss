"""Tests for verify dispatcher."""
from pathlib import Path
import pytest

from agent_weiss.lib.contract import Status
from agent_weiss.lib.verify.dispatch import run_all_checks
from agent_weiss.lib.state import State


REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLE = REPO_ROOT


def test_run_all_checks_against_pass_fixture(tmp_path: Path):
    """Run universal controls against a fixture project containing all required files."""
    # Build a project that satisfies all 8 universal controls.
    (tmp_path / "AGENTS.md").write_text("# agent instructions\n")
    (tmp_path / "CLAUDE.md").write_text("# claude instructions\n")
    (tmp_path / "README.md").write_text("# project\n")
    (tmp_path / ".gitignore").write_text(".env\n.env.*\n")
    (tmp_path / "LICENSE").write_text("MIT\n")
    (tmp_path / ".pre-commit-config.yaml").write_text("repos:\n  - repo: https://github.com/gitleaks/gitleaks\n    hooks:\n      - id: gitleaks\n")
    # No .env files in tree — env-files-not-tracked passes.

    state = State(profiles=["universal"])
    results = run_all_checks(
        project_root=tmp_path,
        bundle_root=BUNDLE,
        state=state,
    )

    assert len(results) == 8
    by_id = {r.control_id: r for r in results}

    # Pure shell controls should all pass.
    assert by_id["universal.docs.agents-md-present"].status is Status.PASS
    assert by_id["universal.docs.claude-md-present"].status is Status.PASS
    assert by_id["universal.docs.readme-present"].status is Status.PASS
    assert by_id["universal.security.env-files-not-tracked"].status is Status.PASS
    assert by_id["universal.security.gitleaks-precommit"].status is Status.PASS
    assert by_id["universal.vcs.gitignore-present"].status is Status.PASS
    assert by_id["universal.vcs.license-present"].status is Status.PASS

    # gitignore-secrets is a Rego control — passes if conftest is installed
    # AND .gitignore has both .env and .env.*. Status should be pass or setup-unmet
    # depending on whether conftest is available.
    assert by_id["universal.security.gitignore-secrets"].status in (Status.PASS, Status.SETUP_UNMET)


def test_run_all_checks_against_empty_fixture(tmp_path: Path):
    """Run against an empty project — most controls fail, none crash."""
    state = State(profiles=["universal"])
    results = run_all_checks(
        project_root=tmp_path,
        bundle_root=BUNDLE,
        state=state,
    )
    assert len(results) == 8
    # Every result has a parsed status (no exceptions).
    for r in results:
        assert r.status in (Status.PASS, Status.FAIL, Status.SETUP_UNMET)


def test_run_all_checks_filters_by_state_profiles(tmp_path: Path):
    """profiles=['python'] runs only the 5 python controls."""
    state = State(profiles=["python"])
    results = run_all_checks(
        project_root=tmp_path,
        bundle_root=BUNDLE,
        state=state,
    )
    assert len(results) == 5
    assert {r.profile for r in results} == {"python"}


def test_run_all_checks_sets_profile_and_domain(tmp_path: Path):
    """Each result carries profile + domain derived from the control id."""
    state = State(profiles=["universal"])
    results = run_all_checks(
        project_root=tmp_path,
        bundle_root=BUNDLE,
        state=state,
    )
    for r in results:
        parts = r.control_id.split(".")
        assert r.profile == parts[0]
        assert r.domain == parts[1]


def test_run_all_checks_handles_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A check.sh that exceeds the timeout yields setup-unmet, not an exception."""
    import subprocess as _sp

    real_run = _sp.run

    def fake_run(*args, **kwargs):
        # Any invocation of check.sh under the timeout raises TimeoutExpired.
        if args and isinstance(args[0], list) and args[0][:1] == ["sh"]:
            raise _sp.TimeoutExpired(cmd=args[0], timeout=kwargs.get("timeout", 0))
        return real_run(*args, **kwargs)

    monkeypatch.setattr("agent_weiss.lib.verify.dispatch.subprocess.run", fake_run)

    state = State(profiles=["universal"])
    results = run_all_checks(
        project_root=tmp_path,
        bundle_root=BUNDLE,
        state=state,
        timeout=0.01,
    )
    assert len(results) == 8
    for r in results:
        assert r.status is Status.SETUP_UNMET
        assert "timed out" in r.summary.lower()
