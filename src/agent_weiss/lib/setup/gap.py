"""Gap analysis: walk applicable controls, emit Proposals.

In v1 (Plan 3), every applicable control that isn't already overridden becomes
a MANUAL_ACTION proposal. Plan 4 will tighten this to be driven by check.sh
results (only failing or setup-unmet controls become proposals).
"""
from __future__ import annotations
from pathlib import Path

from ruamel.yaml import YAML

from agent_weiss.lib.state import State
from agent_weiss.lib.schemas import validate_prescribed
from agent_weiss.lib.setup.types import Proposal, ActionKind


def compute_proposals(
    project_root: Path,
    bundle_root: Path,
    state: State,
) -> list[Proposal]:
    """Walk the bundle's profiles tree and emit a Proposal per applicable control.

    Skips controls whose id is already in state.overrides.
    """
    yaml = YAML(typ="safe")
    proposals: list[Proposal] = []

    profiles_root = bundle_root / "profiles"
    for prescribed_path in profiles_root.rglob("prescribed.yaml"):
        data = yaml.load(prescribed_path)
        if data is None:
            continue
        prescribed = validate_prescribed(data)

        # Filter by enabled profiles.
        profile = prescribed.id.split(".")[0]
        if profile not in state.profiles:
            continue

        # Skip already-overridden controls.
        if prescribed.id in state.overrides:
            continue

        # Skip controls whose applies_to doesn't match enabled profiles.
        # 'any' is always applicable; otherwise the profile must be in the list.
        if "any" not in prescribed.applies_to and profile not in prescribed.applies_to:
            continue

        domain = prescribed.id.split(".")[1]
        control_dir = prescribed_path.parent
        instruct_path = control_dir / "instruct.md"

        proposals.append(Proposal(
            control_id=prescribed.id,
            profile=profile,
            domain=domain,
            action_kind=ActionKind.MANUAL_ACTION,
            summary=prescribed.what.strip().splitlines()[0],
            instruct_path=instruct_path if instruct_path.exists() else None,
            depends_on=list(prescribed.depends_on),
        ))

    proposals.sort(key=lambda p: p.control_id)
    return proposals
