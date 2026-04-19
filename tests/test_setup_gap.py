"""Tests for compute_proposals gap analysis."""
from pathlib import Path
import pytest

from agent_weiss.lib.setup.gap import compute_proposals
from agent_weiss.lib.setup.types import Proposal, ActionKind, OverrideEntry
from agent_weiss.lib.state import State


REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLE = REPO_ROOT  # use the agent-weiss repo itself as bundle for tests


def test_compute_proposals_for_universal_profile_only():
    """With profiles=['universal'], proposals cover the 8 universal controls only."""
    state = State(profiles=["universal"])
    proposals = compute_proposals(
        project_root=Path("/tmp/fake-project"),
        bundle_root=BUNDLE,
        state=state,
    )
    profiles = {p.profile for p in proposals}
    assert profiles == {"universal"}
    # Plan 1's agents-md-present + Plan 2's 7 universal controls = 8
    assert len(proposals) == 8


def test_compute_proposals_for_python_profile():
    """profiles=['python'] returns exactly the 5 python controls."""
    state = State(profiles=["python"])
    proposals = compute_proposals(
        project_root=Path("/tmp/fake-project"),
        bundle_root=BUNDLE,
        state=state,
    )
    profiles = {p.profile for p in proposals}
    assert profiles == {"python"}
    assert len(proposals) == 5


def test_compute_proposals_skips_overridden():
    """Controls already in state.overrides are excluded from proposals."""
    state = State(
        profiles=["python"],
        overrides={
            "python.quality.ty-config": OverrideEntry(
                reason="we use mypy",
                decided_at="2026-04-19",
            ),
        },
    )
    proposals = compute_proposals(
        project_root=Path("/tmp/fake-project"),
        bundle_root=BUNDLE,
        state=state,
    )
    ids = {p.control_id for p in proposals}
    assert "python.quality.ty-config" not in ids
    assert len(proposals) == 4


def test_proposals_are_manual_action_in_v1():
    """Plan 3 emits only MANUAL_ACTION proposals."""
    state = State(profiles=["universal"])
    proposals = compute_proposals(
        project_root=Path("/tmp/fake-project"),
        bundle_root=BUNDLE,
        state=state,
    )
    assert all(p.action_kind == ActionKind.MANUAL_ACTION for p in proposals)


def test_proposal_carries_instruct_path():
    """Each proposal points at its control's instruct.md."""
    state = State(profiles=["universal"])
    proposals = compute_proposals(
        project_root=Path("/tmp/fake-project"),
        bundle_root=BUNDLE,
        state=state,
    )
    for p in proposals:
        assert p.instruct_path is not None
        assert p.instruct_path.exists(), f"missing {p.instruct_path}"
        assert p.instruct_path.name == "instruct.md"


def test_proposal_carries_depends_on():
    """If prescribed.yaml declares depends_on, the proposal carries it through."""
    # None of v1 controls declare depends_on, so this just verifies the field
    # is populated (empty list is fine).
    state = State(profiles=["python"])
    proposals = compute_proposals(
        project_root=Path("/tmp/fake-project"),
        bundle_root=BUNDLE,
        state=state,
    )
    for p in proposals:
        assert isinstance(p.depends_on, list)
