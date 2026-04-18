"""Tests for bundle.yaml schema validation."""
import pytest
from agent_weiss.lib.schemas import validate_bundle, BundleSchema


def test_bundle_minimal_valid():
    """A minimal bundle.yaml has version, files."""
    data = {
        "version": "0.0.1",
        "files": {
            "profiles/universal/domains/docs/controls/agents-md-present/policy.rego": "abc123",
            "profiles/universal/domains/docs/controls/agents-md-present/check.sh": "def456",
        },
    }
    result = validate_bundle(data)
    assert isinstance(result, BundleSchema)
    assert result.version == "0.0.1"
    assert len(result.files) == 2


def test_bundle_lookup_file_hash():
    """BundleSchema.hash_for(path) returns the recorded sha256 or None."""
    data = {
        "version": "0.0.1",
        "files": {"a/b/c.rego": "abc123"},
    }
    bundle = validate_bundle(data)
    assert bundle.hash_for("a/b/c.rego") == "abc123"
    assert bundle.hash_for("missing/file.rego") is None


def test_bundle_missing_version_raises():
    """Missing version field raises ValueError."""
    data = {"files": {}}
    with pytest.raises(ValueError, match="version"):
        validate_bundle(data)


def test_bundle_files_must_be_mapping():
    """files must be a dict (path → sha256), not a list."""
    data = {"version": "0.0.1", "files": ["a/b.rego"]}
    with pytest.raises(ValueError, match="files"):
        validate_bundle(data)
