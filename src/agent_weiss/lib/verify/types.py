"""Verify result types."""
from __future__ import annotations
from dataclasses import dataclass

from agent_weiss.lib.contract import Status


@dataclass(frozen=True)
class ControlResult:
    """Outcome of running one control's check.sh.

    Composed from the control's identifying triple (id, profile, domain) plus
    the parsed check.sh output (status, summary, findings_count, install,
    details_path). One ControlResult per control per verify run.
    """
    control_id: str
    profile: str
    domain: str
    status: Status
    summary: str
    findings_count: int = 0
    install: str | None = None
    details_path: str | None = None
