"""Detect anomalies between .agent-weiss.yaml state and project disk reality.

Returns a structured report. Interactive prompting (the user-facing 'what
should I do about this?' flow) is layered on top by skill.md / Plan 3.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from agent_weiss.lib.state import State, read_state
from agent_weiss.lib.hashing import sha256_file


AnomalyKind = Literal["orphan", "ghost", "locally_modified"]

POLICIES_DIR = ".agent-weiss/policies"


@dataclass(frozen=True)
class Anomaly:
    kind: AnomalyKind
    path: str
    detail: str = ""


@dataclass
class ReconcileReport:
    anomalies: list[Anomaly] = field(default_factory=list)


def reconcile(project_root: Path) -> ReconcileReport:
    """Compare state against disk; return a list of anomalies (no prompting)."""
    state = read_state(project_root)
    report = ReconcileReport()

    # 1. Detect ghosts (tracked but missing) and locally-modified (tracked, hash mismatch).
    for relative_path, entry in state.prescribed_files.items():
        full_path = project_root / relative_path
        if not full_path.exists():
            report.anomalies.append(Anomaly(
                kind="ghost",
                path=relative_path,
                detail=f"recorded sha256 {entry.sha256[:8]}, file missing",
            ))
            continue

        actual_hash = sha256_file(full_path)
        if actual_hash != entry.sha256:
            report.anomalies.append(Anomaly(
                kind="locally_modified",
                path=relative_path,
                detail=f"recorded {entry.sha256[:8]}, on disk {actual_hash[:8]}",
            ))

    # 2. Detect orphans (in policies dir, not tracked).
    policies_dir = project_root / POLICIES_DIR
    if policies_dir.exists():
        for entry_path in policies_dir.iterdir():
            if not entry_path.is_file():
                continue
            relative_path = str(entry_path.relative_to(project_root))
            if relative_path not in state.prescribed_files:
                report.anomalies.append(Anomaly(
                    kind="orphan",
                    path=relative_path,
                    detail="present on disk, not in prescribed_files",
                ))

    return report
