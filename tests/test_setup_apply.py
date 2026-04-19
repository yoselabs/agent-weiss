"""Tests for apply_proposal (manual_action path)."""
from pathlib import Path
from agent_weiss.lib.state import State
from agent_weiss.lib.setup.types import Proposal, ActionKind, OverrideEntry
from agent_weiss.lib.setup.apply import apply_proposal, ApplyOutcome


def _proposal(cid: str = "universal.docs.claude-md-present") -> Proposal:
    return Proposal(
        control_id=cid,
        profile=cid.split(".")[0],
        domain=cid.split(".")[1],
        action_kind=ActionKind.MANUAL_ACTION,
        summary="x",
    )


def test_apply_approved_is_noop_for_state():
    state = State(profiles=["universal"])
    p = _proposal()
    new_state, outcome = apply_proposal(
        proposal=p,
        state=state,
        outcome=ApplyOutcome.APPROVED,
        decided_at="2026-04-19",
    )
    assert outcome == ApplyOutcome.APPROVED
    assert new_state.overrides == {}


def test_apply_skipped_no_reason_is_noop():
    state = State(profiles=["universal"])
    p = _proposal()
    new_state, _ = apply_proposal(
        proposal=p,
        state=state,
        outcome=ApplyOutcome.SKIPPED,
        decided_at="2026-04-19",
    )
    assert new_state.overrides == {}


def test_apply_skipped_with_reason_records_override():
    state = State(profiles=["python"])
    p = _proposal("python.quality.ty-config")
    new_state, _ = apply_proposal(
        proposal=p,
        state=state,
        outcome=ApplyOutcome.SKIPPED,
        decided_at="2026-04-19",
        reason="we use mypy",
    )
    assert "python.quality.ty-config" in new_state.overrides
    assert new_state.overrides["python.quality.ty-config"].reason == "we use mypy"
    assert new_state.overrides["python.quality.ty-config"].decided_at == "2026-04-19"


def test_apply_does_not_mutate_input_state():
    state = State(profiles=["python"])
    p = _proposal("python.quality.ty-config")
    apply_proposal(
        proposal=p,
        state=state,
        outcome=ApplyOutcome.SKIPPED,
        decided_at="2026-04-19",
        reason="we use mypy",
    )
    assert state.overrides == {}  # original untouched


def test_apply_install_file_kind_raises_not_implemented():
    """Plan 3 doesn't implement INSTALL_FILE; calling it raises NotImplementedError."""
    import pytest
    p = Proposal(
        control_id="x.y.z",
        profile="x",
        domain="y",
        action_kind=ActionKind.INSTALL_FILE,
        summary="install x",
    )
    state = State(profiles=["x"])
    with pytest.raises(NotImplementedError, match="install_file"):
        apply_proposal(
            proposal=p,
            state=state,
            outcome=ApplyOutcome.APPROVED,
            decided_at="2026-04-19",
        )
