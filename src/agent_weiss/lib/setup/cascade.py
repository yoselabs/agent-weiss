"""depends_on cascade: when a control's dependency is skipped, skip it too.

Iterative algorithm:
1. Build set of skipped control_ids from decision.skip_indices.
2. For each proposal, if any of its depends_on is skipped, mark it skipped
   too (with a synthesized reason).
3. Repeat until no new skips.

Then re-render the Decision.
"""
from __future__ import annotations
from dataclasses import replace

from agent_weiss.lib.setup.types import Proposal, Decision


def cascade_skips(
    *,
    proposals: list[Proposal],
    decision: Decision,
) -> Decision:
    """Return a new Decision with cascaded skips applied.

    Approve_indices that depend on a skipped control are moved to skip_indices
    with a synthesized reason like "cascaded skip — depends on X (skipped)".
    """
    # 1-based index → control_id
    by_index = {i + 1: p for i, p in enumerate(proposals)}

    skip_indices = list(decision.skip_indices)
    skip_reasons = dict(decision.skip_reasons)
    approve_indices = list(decision.approve_indices)

    skipped_ids = {by_index[i].control_id for i in skip_indices if i in by_index}

    changed = True
    while changed:
        changed = False
        for i, p in by_index.items():
            if i in skip_indices:
                continue
            for dep in p.depends_on:
                if dep in skipped_ids:
                    skip_indices.append(i)
                    skip_reasons[i] = f"cascaded skip — depends on {dep} (skipped)"
                    if i in approve_indices:
                        approve_indices.remove(i)
                    skipped_ids.add(p.control_id)
                    changed = True
                    break

    return replace(
        decision,
        approve_indices=sorted(set(approve_indices)),
        skip_indices=sorted(set(skip_indices)),
        skip_reasons=skip_reasons,
    )
