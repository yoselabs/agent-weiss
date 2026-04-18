"""Tests for the shared Rego runner helper."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from agent_weiss.lib.rego import run_rego_check


REPO_ROOT = Path(__file__).resolve().parent.parent


def _conftest_available() -> bool:
    return shutil.which("conftest") is not None


@pytest.mark.skipif(not _conftest_available(), reason="conftest not installed")
def test_rego_pass(tmp_path: Path):
    """Project file satisfies the policy → status=pass, exit 0."""
    policy = tmp_path / "policy.rego"
    policy.write_text(
        "package x\n"
        "import rego.v1\n"
        "deny contains msg if {\n"
        "  not input.foo\n"
        "  msg := \"missing foo\"\n"
        "}\n"
    )
    target = tmp_path / "input.json"
    target.write_text(json.dumps({"foo": "bar"}))

    result = run_rego_check(target=target, policy=policy)
    assert result["status"] == "pass"
    assert result["findings_count"] == 0


@pytest.mark.skipif(not _conftest_available(), reason="conftest not installed")
def test_rego_fail_with_findings(tmp_path: Path):
    """Project file violates policy → status=fail, findings_count matches deny count."""
    policy = tmp_path / "policy.rego"
    policy.write_text(
        "package x\n"
        "import rego.v1\n"
        "deny contains msg if {\n"
        "  not input.foo\n"
        "  msg := \"missing foo\"\n"
        "}\n"
        "deny contains msg if {\n"
        "  not input.bar\n"
        "  msg := \"missing bar\"\n"
        "}\n"
    )
    target = tmp_path / "input.json"
    target.write_text("{}")

    result = run_rego_check(target=target, policy=policy)
    assert result["status"] == "fail"
    assert result["findings_count"] == 2
    assert "missing foo" in result["summary"] or "missing bar" in result["summary"]


def test_rego_setup_unmet_when_conftest_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """If conftest binary not found, return setup-unmet with install hint."""
    monkeypatch.setenv("PATH", "")
    policy = tmp_path / "policy.rego"
    policy.write_text("package x\nimport rego.v1\n")
    target = tmp_path / "input.json"
    target.write_text("{}")

    result = run_rego_check(target=target, policy=policy)
    assert result["status"] == "setup-unmet"
    assert "conftest" in result["install"].lower()


def test_rego_target_missing_returns_pass(tmp_path: Path):
    """If the target file doesn't exist (control not relevant), return pass with explanation."""
    policy = tmp_path / "policy.rego"
    policy.write_text("package x\nimport rego.v1\n")
    target = tmp_path / "nonexistent.json"

    result = run_rego_check(target=target, policy=policy)
    assert result["status"] == "pass"
    assert "not present" in result["summary"].lower() or "skipped" in result["summary"].lower()
