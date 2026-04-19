"""Tests for proposal batching + rendering."""
from pathlib import Path
from agent_weiss.lib.setup.types import Proposal, ActionKind
from agent_weiss.lib.setup.batch import batch_by_domain, render_proposals


def _proposal(cid: str, profile: str, domain: str, summary: str = "x") -> Proposal:
    return Proposal(
        control_id=cid,
        profile=profile,
        domain=domain,
        action_kind=ActionKind.MANUAL_ACTION,
        summary=summary,
    )


def test_batch_by_domain_groups_in_input_order():
    """Proposals are grouped by domain; domain key insertion order matches first-seen."""
    proposals = [
        _proposal("universal.docs.a", "universal", "docs"),
        _proposal("universal.security.b", "universal", "security"),
        _proposal("universal.docs.c", "universal", "docs"),
    ]
    batched = batch_by_domain(proposals)
    assert list(batched.keys()) == ["docs", "security"]
    assert len(batched["docs"]) == 2
    assert len(batched["security"]) == 1


def test_render_proposals_numbers_globally():
    """Numbers run 1..N across all domains in the rendered text."""
    proposals = [
        _proposal("universal.docs.a", "universal", "docs", "create AGENTS.md"),
        _proposal("universal.security.b", "universal", "security", "gitignore .env"),
        _proposal("universal.docs.c", "universal", "docs", "create CLAUDE.md"),
    ]
    text = render_proposals(proposals)
    assert "1." in text
    assert "2." in text
    assert "3." in text
    assert "create AGENTS.md" in text
    assert "create CLAUDE.md" in text
    assert "docs" in text.lower()
    assert "security" in text.lower()


def test_render_proposals_groups_under_domain_headers():
    """The rendered text has a header per domain, with that domain's items
    listed under it before the next domain begins."""
    proposals = [
        _proposal("universal.docs.a", "universal", "docs", "create AGENTS.md"),
        _proposal("universal.security.b", "universal", "security", "gitignore .env"),
        _proposal("universal.docs.c", "universal", "docs", "create CLAUDE.md"),
    ]
    text = render_proposals(proposals)
    docs_pos = text.lower().index("docs")
    security_pos = text.lower().index("security")
    a_pos = text.index("create AGENTS.md")
    c_pos = text.index("create CLAUDE.md")
    b_pos = text.index("gitignore .env")
    assert docs_pos < a_pos < c_pos < security_pos < b_pos


def test_render_empty_proposals():
    """Empty list renders to a sensible message, not an error."""
    text = render_proposals([])
    assert text.strip()
