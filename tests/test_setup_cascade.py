"""Tests for depends_on cascade."""
from agent_weiss.lib.setup.types import Proposal, ActionKind, Decision
from agent_weiss.lib.setup.cascade import cascade_skips


def _proposal(cid: str, depends_on: list[str] | None = None) -> Proposal:
    return Proposal(
        control_id=cid,
        profile=cid.split(".")[0],
        domain=cid.split(".")[1],
        action_kind=ActionKind.MANUAL_ACTION,
        summary="x",
        depends_on=depends_on or [],
    )


def test_no_dependencies_no_cascade():
    """If no proposal has depends_on, decision is unchanged."""
    proposals = [_proposal("a.b.c"), _proposal("a.b.d")]
    decision = Decision(approve_indices=[1], skip_indices=[2])
    result = cascade_skips(proposals=proposals, decision=decision)
    assert result.approve_indices == [1]
    assert result.skip_indices == [2]


def test_cascade_skips_dependent_when_dependency_skipped():
    """If Y depends on X and X is skipped, Y is auto-skipped with cascade reason."""
    proposals = [
        _proposal("a.b.x"),
        _proposal("a.b.y", depends_on=["a.b.x"]),
        _proposal("a.b.z"),
    ]
    # User skips index 1 (a.b.x); index 2 (a.b.y) should also be skipped.
    decision = Decision(skip_indices=[1], approve_indices=[3])
    result = cascade_skips(proposals=proposals, decision=decision)
    assert 2 in result.skip_indices
    assert 2 in result.skip_reasons
    assert "a.b.x" in result.skip_reasons[2].lower()


def test_cascade_does_not_remove_explicit_approval():
    """If user explicitly approved Y but X is skipped, Y still gets cascade-skipped (override safety)."""
    proposals = [
        _proposal("a.b.x"),
        _proposal("a.b.y", depends_on=["a.b.x"]),
    ]
    decision = Decision(skip_indices=[1], approve_indices=[2])
    result = cascade_skips(proposals=proposals, decision=decision)
    # Y moved from approve to skip
    assert 2 not in result.approve_indices
    assert 2 in result.skip_indices


def test_cascade_does_not_affect_already_skipped():
    """Already-skipped items stay skipped; their existing reasons are preserved."""
    proposals = [
        _proposal("a.b.x"),
        _proposal("a.b.y", depends_on=["a.b.x"]),
    ]
    decision = Decision(
        skip_indices=[1, 2],
        skip_reasons={2: "user reason"},
    )
    result = cascade_skips(proposals=proposals, decision=decision)
    assert result.skip_reasons[2] == "user reason"


def test_transitive_cascade():
    """If A→B→C and A is skipped, both B and C are cascaded."""
    proposals = [
        _proposal("a.b.A"),
        _proposal("a.b.B", depends_on=["a.b.A"]),
        _proposal("a.b.C", depends_on=["a.b.B"]),
    ]
    decision = Decision(skip_indices=[1], approve_indices=[2, 3])
    result = cascade_skips(proposals=proposals, decision=decision)
    assert 2 in result.skip_indices
    assert 3 in result.skip_indices
