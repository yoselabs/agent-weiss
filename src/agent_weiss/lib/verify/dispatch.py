"""Run every applicable control's check.sh; collect ControlResults.

For each control in the bundle whose profile matches state.profiles AND whose
applies_to allows it, invoke check.sh with cwd=project_root and env including
AGENT_WEISS_BUNDLE pointing at bundle_root. Parse the output via the contract
parser, build a ControlResult, append to the list.

Each check.sh runs under a per-control subprocess timeout (default 30s). A
timeout or contract violation yields a setup-unmet ControlResult so the verify
pass doesn't crash on one bad control.
"""
from __future__ import annotations
import os
import subprocess
from pathlib import Path

from ruamel.yaml import YAML

from agent_weiss.lib.state import State
from agent_weiss.lib.schemas import validate_prescribed
from agent_weiss.lib.contract import (
    Status,
    parse_check_output,
    ContractError,
)
from agent_weiss.lib.verify.types import ControlResult


DEFAULT_CHECK_TIMEOUT_SECONDS = 30.0


def run_all_checks(
    *,
    project_root: Path,
    bundle_root: Path,
    state: State,
    timeout: float = DEFAULT_CHECK_TIMEOUT_SECONDS,
) -> list[ControlResult]:
    """Run every applicable control's check.sh; return ControlResults sorted by id."""
    yaml = YAML(typ="safe")
    results: list[ControlResult] = []

    profiles_root = bundle_root / "profiles"
    for prescribed_path in profiles_root.rglob("prescribed.yaml"):
        data = yaml.load(prescribed_path)
        if data is None:
            continue
        prescribed = validate_prescribed(data)

        profile = prescribed.id.split(".")[0]
        domain = prescribed.id.split(".")[1]

        # Filter by enabled profiles.
        if profile not in state.profiles:
            continue

        # Filter by applies_to: 'any' OR matches profile.
        if "any" not in prescribed.applies_to and profile not in prescribed.applies_to:
            continue

        check_sh = prescribed_path.parent / "check.sh"
        if not check_sh.exists():
            results.append(ControlResult(
                control_id=prescribed.id,
                profile=profile,
                domain=domain,
                status=Status.SETUP_UNMET,
                summary=f"check.sh missing at {check_sh}",
            ))
            continue

        env = {**os.environ, "AGENT_WEISS_BUNDLE": str(bundle_root)}
        try:
            proc = subprocess.run(
                ["sh", str(check_sh)],
                cwd=project_root,
                capture_output=True,
                text=True,
                env=env,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            results.append(ControlResult(
                control_id=prescribed.id,
                profile=profile,
                domain=domain,
                status=Status.SETUP_UNMET,
                summary=f"check.sh timed out after {timeout}s",
            ))
            continue

        try:
            parsed = parse_check_output(stdout=proc.stdout, exit_code=proc.returncode)
        except ContractError as e:
            results.append(ControlResult(
                control_id=prescribed.id,
                profile=profile,
                domain=domain,
                status=Status.SETUP_UNMET,
                summary=f"contract violation: {e}",
            ))
            continue

        results.append(ControlResult(
            control_id=prescribed.id,
            profile=profile,
            domain=domain,
            status=parsed.status,
            summary=parsed.summary,
            findings_count=parsed.findings_count,
            install=parsed.install,
            details_path=parsed.details_path,
        ))

    results.sort(key=lambda r: r.control_id)
    return results
