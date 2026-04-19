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


import copy
from agent_weiss.lib.state import SCHEMA_VERSION


def test_state_schema_version_round_trips(tmp_path):
    """State.schema_version is read from disk and re-written on round-trip."""
    state_path = tmp_path / ".agent-weiss.yaml"
    state_path.write_text("version: 1\nbundle_version: '0.0.1'\nprofiles: []\n")
    state = read_state(tmp_path)
    assert state.schema_version == 1
    write_state(tmp_path, state)
    re_read = read_state(tmp_path)
    assert re_read.schema_version == 1


def test_state_unknown_schema_version_raises(tmp_path):
    """Reading a state file with a schema_version newer than supported raises."""
    state_path = tmp_path / ".agent-weiss.yaml"
    state_path.write_text(f"version: {SCHEMA_VERSION + 1}\nprofiles: []\n")
    import pytest
    with pytest.raises(ValueError, match="schema_version"):
        read_state(tmp_path)


def test_write_state_does_not_mutate_raw(tmp_path):
    """Calling write_state should not mutate state._raw nested values (deepcopy guarantee)."""
    state_path = tmp_path / ".agent-weiss.yaml"
    state_path.write_text(
        "version: 1\n"
        "profiles: []\n"
        "future_block:\n"
        "  nested:\n"
        "    key: original_value\n"
    )
    state = read_state(tmp_path)
    raw_before = copy.deepcopy(state._raw)
    write_state(tmp_path, state)
    assert state._raw == raw_before


from agent_weiss.lib.setup.types import OverrideEntry


def test_state_overrides_round_trip(tmp_path):
    """Overrides written to state are re-read with same shape."""
    from agent_weiss.lib.state import State, write_state, read_state
    state = State(
        bundle_version="0.0.1",
        profiles=["python"],
        overrides={
            "python.quality.ty-config": OverrideEntry(
                reason="we use mypy",
                decided_at="2026-04-19",
            ),
        },
    )
    write_state(tmp_path, state)
    loaded = read_state(tmp_path)
    assert "python.quality.ty-config" in loaded.overrides
    assert loaded.overrides["python.quality.ty-config"].reason == "we use mypy"
    assert loaded.overrides["python.quality.ty-config"].decided_at == "2026-04-19"


def test_state_overrides_default_empty(tmp_path):
    """A fresh state has empty overrides."""
    from agent_weiss.lib.state import read_state
    assert read_state(tmp_path).overrides == {}
