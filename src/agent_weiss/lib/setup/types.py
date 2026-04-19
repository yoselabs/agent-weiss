"""Core data types for the setup orchestration layer."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ActionKind(Enum):
    """What the setup phase would do for this control if approved.

    MANUAL_ACTION: the only path used in v1 — show instruct.md, ask the user
        to fix it themselves and confirm done. No automatic file changes.
    INSTALL_FILE: stub — copy a bundle file into the project. Reserved for
        future plans when controls ship installable artifacts.
    MERGE_FRAGMENT: stub — merge a config fragment into a target config file.
        Reserved for future plans when controls ship config_fragment payloads
        and format-aware mergers exist.
    """
    MANUAL_ACTION = "manual_action"
    INSTALL_FILE = "install_file"
    MERGE_FRAGMENT = "merge_fragment"


@dataclass(frozen=True)
class Proposal:
    """One proposed setup action for a single control.

    Plan 3 only emits MANUAL_ACTION proposals. The other action_kind values
    are present so the data model doesn't churn when later plans add them.
    """
    control_id: str
    profile: str
    domain: str
    action_kind: ActionKind
    summary: str
    instruct_path: Path | None = None
    depends_on: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Decision:
    """Parsed user decision over a batch of proposals.

    Indices are 1-based as displayed to the user.
    Use `approve_all=True` for "approve all" or `approve_domains=[...]` for
    "approve <domain>". `approve_indices` and `skip_indices` carry explicit
    per-item picks. `explain_index` (if set) means the user asked to explain
    one item; the skill should re-prompt afterward.
    """
    approve_all: bool = False
    approve_domains: list[str] = field(default_factory=list)
    approve_indices: list[int] = field(default_factory=list)
    skip_indices: list[int] = field(default_factory=list)
    skip_reasons: dict[int, str] = field(default_factory=dict)
    explain_index: int | None = None
    dry_run: bool = False
    cancel: bool = False


@dataclass
class OverrideEntry:
    """A control was deliberately declined with a stated reason.

    Recorded under State.overrides[control_id]. Counts as 'pass' in the Setup
    score (Plan 4) per the roadmap's 'Override = pass' rule.
    """
    reason: str
    decided_at: str  # ISO date
