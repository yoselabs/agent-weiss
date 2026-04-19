"""Backup mechanism for setup writes.

Before any setup action overwrites a project file, the file is copied to
`.agent-weiss/backups/<timestamp>/<relative_path>`. Reversible by copying back.

Plan 3's MANUAL_ACTION path doesn't write files (so doesn't backup), but this
helper is built now so future INSTALL_FILE and MERGE_FRAGMENT paths can use it.
"""
from __future__ import annotations
import shutil
from pathlib import Path


BACKUPS_SUBDIR = ".agent-weiss/backups"


def backup_file(*, project_root: Path, target: Path, timestamp: str) -> Path | None:
    """Copy `target` into the backups dir, returning the backup path.

    Returns None if `target` doesn't exist (no-op).
    Raises ValueError if `target` is outside `project_root`.
    """
    if not target.exists():
        return None

    try:
        relative = target.resolve().relative_to(project_root.resolve())
    except ValueError as e:
        raise ValueError(
            f"target {target} is outside project {project_root}"
        ) from e

    backup_dir = project_root / BACKUPS_SUBDIR / timestamp
    backup_path = backup_dir / relative
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(target, backup_path)
    return backup_path
