"""Tests for dry-run report generator."""
from pathlib import Path
from agent_weiss.lib.setup.types import Proposal, ActionKind
from agent_weiss.lib.setup.dry_run import write_dry_run_report


def _proposal(cid: str, summary: str = "x") -> Proposal:
    return Proposal(
        control_id=cid,
        profile=cid.split(".")[0],
        domain=cid.split(".")[1],
        action_kind=ActionKind.MANUAL_ACTION,
        summary=summary,
    )


def test_write_dry_run_report_creates_file(tmp_path: Path):
    proposals = [
        _proposal("universal.docs.agents-md-present", "ensure AGENTS.md present"),
        _proposal("universal.security.gitignore-secrets", ".env in .gitignore"),
    ]
    path = write_dry_run_report(
        project_root=tmp_path,
        proposals=proposals,
        timestamp="2026-04-19T12-00-00",
    )
    assert path == tmp_path / ".agent-weiss" / "dry-run-2026-04-19T12-00-00.md"
    assert path.exists()


def test_dry_run_report_lists_all_proposals(tmp_path: Path):
    proposals = [
        _proposal("universal.docs.agents-md-present", "ensure AGENTS.md present"),
        _proposal("universal.security.gitignore-secrets", ".env in .gitignore"),
    ]
    path = write_dry_run_report(
        project_root=tmp_path,
        proposals=proposals,
        timestamp="2026-04-19T12-00-00",
    )
    text = path.read_text()
    assert "agents-md-present" in text
    assert "gitignore-secrets" in text
    assert "ensure AGENTS.md present" in text
    assert ".env in .gitignore" in text


def test_dry_run_report_groups_by_domain(tmp_path: Path):
    proposals = [
        _proposal("universal.docs.a", "x"),
        _proposal("universal.security.b", "y"),
        _proposal("universal.docs.c", "z"),
    ]
    path = write_dry_run_report(
        project_root=tmp_path,
        proposals=proposals,
        timestamp="2026-04-19T12-00-00",
    )
    text = path.read_text()
    docs_pos = text.lower().index("docs")
    security_pos = text.lower().index("security")
    assert docs_pos < security_pos


def test_dry_run_report_with_no_proposals(tmp_path: Path):
    path = write_dry_run_report(
        project_root=tmp_path,
        proposals=[],
        timestamp="2026-04-19T12-00-00",
    )
    assert path.exists()
    assert "no proposals" in path.read_text().lower() or "nothing to do" in path.read_text().lower()
