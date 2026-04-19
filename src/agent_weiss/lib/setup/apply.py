"""Apply a single proposal to state.

Plan 3 implements only ActionKind.MANUAL_ACTION:
- APPROVED: no state change (the next verify will check the project).
- SKIPPED without reason: no state change.
- SKIPPED with reason: record an OverrideEntry in state.overrides.

INSTALL_FILE and MERGE_FRAGMENT raise NotImplementedError until later plans
add the file-copy and config-merge logic.
"""
from __future__ import annotations
import copy
from dataclasses import replace
from enum import Enum

from agent_weiss.lib.state import State
from agent_weiss.lib.setup.types import Proposal, ActionKind, OverrideEntry


class ApplyOutcome(Enum):
    APPROVED = "approved"
    SKIPPED = "skipped"


def apply_proposal(
    *,
    proposal: Proposal,
    state: State,
    outcome: ApplyOutcome,
    decided_at: str,
    reason: str | None = None,
) -> tuple[State, ApplyOutcome]:
    """Apply a proposal to state. Returns (new_state, outcome).

    The input state is not mutated; a new State is returned with any overrides
    update applied.
    """
    if proposal.action_kind == ActionKind.INSTALL_FILE:
        raise NotImplementedError(
            "install_file action_kind is not implemented in Plan 3"
        )
    if proposal.action_kind == ActionKind.MERGE_FRAGMENT:
        raise NotImplementedError(
            "merge_fragment action_kind is not implemented in Plan 3"
        )

    # MANUAL_ACTION:
    if outcome == ApplyOutcome.APPROVED:
        return state, outcome
    if outcome == ApplyOutcome.SKIPPED and not reason:
        return state, outcome

    # SKIPPED with reason → record override.
    new_overrides = dict(state.overrides)
    new_overrides[proposal.control_id] = OverrideEntry(
        reason=reason or "",
        decided_at=decided_at,
    )
    new_state = replace(state, overrides=new_overrides, _raw=copy.deepcopy(state._raw))
    return new_state, outcome
