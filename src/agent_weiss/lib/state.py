"""Read and write .agent-weiss.yaml at the project root.

The state file is the source of truth for prescribed-vs-custom file classification.
Round-trips with ruamel.yaml to preserve comments and unknown keys (forward-compat).
"""
from __future__ import annotations
import copy
from dataclasses import dataclass, field
from pathlib import Path
from ruamel.yaml import YAML

from agent_weiss.lib.setup.types import OverrideEntry

STATE_FILENAME = ".agent-weiss.yaml"
SCHEMA_VERSION = 1


@dataclass
class PrescribedFileEntry:
    """One entry in prescribed_files: hash + bundle origin + last sync date."""
    sha256: str
    bundle_path: str
    last_synced: str  # ISO date


@dataclass
class State:
    """In-memory representation of .agent-weiss.yaml.

    Only the fields the skeleton reads are typed here; unknown top-level keys
    are preserved verbatim via the _raw shadow dict for forward compatibility.
    """
    bundle_version: str | None = None
    schema_version: int = SCHEMA_VERSION
    profiles: list[str] = field(default_factory=list)
    prescribed_files: dict[str, PrescribedFileEntry] = field(default_factory=dict)
    overrides: dict[str, OverrideEntry] = field(default_factory=dict)
    _raw: dict = field(default_factory=dict, repr=False)


def _yaml() -> YAML:
    """Configured ruamel.yaml instance for round-trip preservation."""
    y = YAML()
    y.preserve_quotes = True
    y.width = 4096  # avoid line-wrapping long values
    return y


def read_state(project_root: Path) -> State:
    """Read .agent-weiss.yaml from project root. Returns empty State if missing.

    Raises ValueError if state file's schema_version is newer than this code supports.
    """
    path = project_root / STATE_FILENAME
    if not path.exists():
        return State()

    yaml = _yaml()
    raw = yaml.load(path) or {}

    raw_version = raw.get("version", SCHEMA_VERSION)
    if raw_version > SCHEMA_VERSION:
        raise ValueError(
            f"schema_version {raw_version} is newer than supported "
            f"({SCHEMA_VERSION}). Upgrade agent-weiss."
        )

    pf = {}
    for key, entry in (raw.get("prescribed_files") or {}).items():
        pf[str(key)] = PrescribedFileEntry(
            sha256=str(entry["sha256"]),
            bundle_path=str(entry["bundle_path"]),
            last_synced=str(entry["last_synced"]),
        )

    overrides = {}
    for control_id, entry in (raw.get("overrides") or {}).items():
        overrides[str(control_id)] = OverrideEntry(
            reason=str(entry["reason"]),
            decided_at=str(entry["decided_at"]),
        )

    return State(
        bundle_version=raw.get("bundle_version"),
        schema_version=int(raw_version),
        profiles=list(raw.get("profiles") or []),
        prescribed_files=pf,
        overrides=overrides,
        _raw=dict(raw),
    )


def write_state(project_root: Path, state: State) -> None:
    """Write State back to .agent-weiss.yaml, preserving unknown keys.

    Strategy: start from a deepcopy of state._raw (preserves comments + unknown
    fields, but prevents write-time mutation of the in-memory shadow), overlay
    typed fields. This is the source of forward compatibility.
    """
    path = project_root / STATE_FILENAME
    yaml = _yaml()

    out = copy.deepcopy(state._raw)
    out["version"] = SCHEMA_VERSION
    if state.bundle_version is not None:
        out["bundle_version"] = state.bundle_version
    out["profiles"] = state.profiles
    out["prescribed_files"] = {
        path_key: {
            "sha256": entry.sha256,
            "bundle_path": entry.bundle_path,
            "last_synced": entry.last_synced,
        }
        for path_key, entry in state.prescribed_files.items()
    }
    out["overrides"] = {
        control_id: {"reason": entry.reason, "decided_at": entry.decided_at}
        for control_id, entry in state.overrides.items()
    }

    with path.open("w") as f:
        yaml.dump(out, f)
