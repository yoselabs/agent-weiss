"""Tests for backup writer."""
from pathlib import Path
import pytest

from agent_weiss.lib.setup.backup import backup_file


def test_backup_creates_timestamped_dir(tmp_path: Path):
    """Backup is written to .agent-weiss/backups/<timestamp>/<relative>."""
    target = tmp_path / "config.toml"
    target.write_text("original content\n")
    backup = backup_file(project_root=tmp_path, target=target, timestamp="2026-04-19T12-00-00")
    assert backup is not None
    assert backup == tmp_path / ".agent-weiss" / "backups" / "2026-04-19T12-00-00" / "config.toml"
    assert backup.exists()
    assert backup.read_text() == "original content\n"


def test_backup_preserves_relative_path(tmp_path: Path):
    """Nested target paths are preserved under the timestamp dir."""
    target = tmp_path / "nested" / "dir" / "file.txt"
    target.parent.mkdir(parents=True)
    target.write_text("nested content\n")
    backup = backup_file(project_root=tmp_path, target=target, timestamp="2026-04-19T12-00-00")
    assert backup == tmp_path / ".agent-weiss" / "backups" / "2026-04-19T12-00-00" / "nested" / "dir" / "file.txt"
    assert backup.read_text() == "nested content\n"


def test_backup_missing_source_returns_none(tmp_path: Path):
    """If target doesn't exist, no backup is written; return None."""
    target = tmp_path / "missing.txt"
    backup = backup_file(project_root=tmp_path, target=target, timestamp="2026-04-19T12-00-00")
    assert backup is None
    assert not (tmp_path / ".agent-weiss" / "backups").exists()


def test_backup_target_outside_project_raises(tmp_path: Path):
    """Refuse to back up files outside the project root."""
    elsewhere = tmp_path.parent / "elsewhere.txt"
    elsewhere.write_text("x")
    try:
        with pytest.raises(ValueError, match="outside project"):
            backup_file(project_root=tmp_path, target=elsewhere, timestamp="x")
    finally:
        elsewhere.unlink()
