"""Tests for the check.sh output contract parser."""
import pytest
from agent_weiss.lib.contract import (
    CheckResult,
    parse_check_output,
    Status,
    ContractError,
)


def test_parse_pass():
    stdout = '{"status": "pass", "findings_count": 0, "summary": "ruff: clean"}'
    result = parse_check_output(stdout=stdout, exit_code=0)
    assert isinstance(result, CheckResult)
    assert result.status is Status.PASS
    assert result.findings_count == 0
    assert result.summary == "ruff: clean"


def test_parse_fail_with_details():
    stdout = (
        '{"status": "fail", "findings_count": 8, "summary": "ruff: 8 issues", '
        '"details_path": "/tmp/x.log"}'
    )
    result = parse_check_output(stdout=stdout, exit_code=1)
    assert result.status is Status.FAIL
    assert result.findings_count == 8
    assert result.details_path == "/tmp/x.log"


def test_parse_setup_unmet():
    stdout = (
        '{"status": "setup-unmet", "summary": "ruff not installed", '
        '"install": "uv add --dev ruff"}'
    )
    result = parse_check_output(stdout=stdout, exit_code=127)
    assert result.status is Status.SETUP_UNMET
    assert result.install == "uv add --dev ruff"


def test_status_exit_code_mismatch_raises():
    """JSON status: pass with exit 1 is a contract violation."""
    stdout = '{"status": "pass", "findings_count": 0, "summary": "x"}'
    with pytest.raises(ContractError, match="exit code"):
        parse_check_output(stdout=stdout, exit_code=1)


def test_invalid_json_raises():
    with pytest.raises(ContractError, match="JSON"):
        parse_check_output(stdout="not json", exit_code=0)


def test_extra_lines_in_stdout_use_last_json_line():
    """Tools may print warnings to stdout; the contract line is the LAST JSON line."""
    stdout = (
        "warning: deprecated config\n"
        '{"status": "pass", "findings_count": 0, "summary": "ok"}\n'
    )
    result = parse_check_output(stdout=stdout, exit_code=0)
    assert result.status is Status.PASS


def test_unknown_status_raises():
    stdout = '{"status": "weird", "summary": "x"}'
    with pytest.raises(ContractError, match="status"):
        parse_check_output(stdout=stdout, exit_code=0)
