"""Tests for .agent-weiss.yaml read/write."""
from pathlib import Path
import pytest
from agent_weiss.lib.state import (
    State,
    read_state,
    write_state,
    PrescribedFileEntry,
)


def test_read_missing_returns_empty_state(tmp_path: Path):
    """Missing .agent-weiss.yaml yields an empty State (first-run scenario)."""
    state = read_state(tmp_path)
    assert state.profiles == []
    assert state.prescribed_files == {}
    assert state.bundle_version is None


def test_write_then_read_roundtrip(tmp_path: Path):
    """A state written and re-read is structurally identical."""
    original = State(
        bundle_version="0.0.1",
        profiles=["universal", "python"],
        prescribed_files={
            ".agent-weiss/policies/universal-docs.rego": PrescribedFileEntry(
                sha256="abc123",
                bundle_path="profiles/universal/domains/docs/controls/agents-md-present/policy.rego",
                last_synced="2026-04-14",
            ),
        },
    )
    write_state(tmp_path, original)
    loaded = read_state(tmp_path)
    assert loaded.bundle_version == "0.0.1"
    assert loaded.profiles == ["universal", "python"]
    assert ".agent-weiss/policies/universal-docs.rego" in loaded.prescribed_files


def test_write_preserves_unknown_keys(tmp_path: Path):
    """Round-trip preserves any unknown top-level keys (forward compatibility)."""
    state_path = tmp_path / ".agent-weiss.yaml"
    state_path.write_text(
        "version: 1\n"
        "bundle_version: '0.0.1'\n"
        "profiles: []\n"
        "future_field: keep_me\n"
    )
    state = read_state(tmp_path)
    write_state(tmp_path, state)
    content = state_path.read_text()
    assert "future_field" in content
    assert "keep_me" in content


def test_state_file_path_is_yaml_at_root(tmp_path: Path):
    """State file lives at <project_root>/.agent-weiss.yaml."""
    state = State(profiles=["universal"])
    write_state(tmp_path, state)
    assert (tmp_path / ".agent-weiss.yaml").exists()
