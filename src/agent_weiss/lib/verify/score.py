"""Setup + Quality score formulas per spec §7.

Setup score: per-control 100 if status is pass/fail OR control is overridden,
else 0. Per-domain mean. Total mean of domains.

Quality score (Task 4): per-control 100 if pass / 0 if fail / EXCLUDED if
setup-unmet. Per-domain mean of measurable. Total mean of domains.
"""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass, field

from agent_weiss.lib.contract import Status
from agent_weiss.lib.setup.types import OverrideEntry
from agent_weiss.lib.verify.types import ControlResult


@dataclass(frozen=True)
class ScoreReport:
    """Computed score breakdown.

    per_control: control_id → score (0..100). Excluded controls (quality
        score with setup-unmet) are absent from this map.
    per_domain: domain → mean of per_control scores in that domain.
    total: mean of per_domain scores. 0.0 when there are no measurable
        controls/domains.
    """
    per_control: dict[str, float] = field(default_factory=dict)
    per_domain: dict[str, float] = field(default_factory=dict)
    total: float = 0.0


def compute_setup_score(
    *,
    results: list[ControlResult],
    overrides: dict[str, OverrideEntry],
) -> ScoreReport:
    """Compute the Setup score per spec §7.

    Per control: 100 if status is pass/fail OR control is in overrides; 0 if
    status is setup-unmet (and not overridden).
    """
    per_control: OrderedDict[str, float] = OrderedDict()
    for r in results:
        if r.control_id in overrides:
            per_control[r.control_id] = 100.0
        elif r.status in (Status.PASS, Status.FAIL):
            per_control[r.control_id] = 100.0
        else:  # SETUP_UNMET
            per_control[r.control_id] = 0.0

    return _aggregate(per_control, results)


def _aggregate(
    per_control: dict[str, float],
    results: list[ControlResult],
) -> ScoreReport:
    """Roll per_control scores up to per_domain mean and total mean."""
    if not per_control:
        return ScoreReport()

    # Build domain → list of scores from per_control.
    by_domain: OrderedDict[str, list[float]] = OrderedDict()
    cid_to_domain = {r.control_id: r.domain for r in results}
    for cid, score in per_control.items():
        domain = cid_to_domain[cid]
        by_domain.setdefault(domain, []).append(score)

    per_domain = {d: sum(s) / len(s) for d, s in by_domain.items()}
    total = sum(per_domain.values()) / len(per_domain)
    return ScoreReport(per_control=dict(per_control), per_domain=per_domain, total=total)
