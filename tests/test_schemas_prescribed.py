"""Tests for prescribed.yaml schema validation."""
import pytest
from agent_weiss.lib.schemas import validate_prescribed, PrescribedSchema


def test_prescribed_minimal_valid():
    """A minimal prescribed.yaml has id, version, what, why, applies_to."""
    data = {
        "id": "universal.docs.agents-md-present",
        "version": 1,
        "what": "Project has an AGENTS.md file at the repository root.",
        "why": "AGENTS.md is the cross-tool standard for instructing AI coding agents.",
        "applies_to": ["any"],
    }
    result = validate_prescribed(data)
    assert isinstance(result, PrescribedSchema)
    assert result.id == "universal.docs.agents-md-present"


def test_prescribed_with_install_per_os():
    """prescribed.yaml may declare install commands per OS."""
    data = {
        "id": "universal.security.gitleaks-configured",
        "version": 1,
        "what": "gitleaks pre-commit hook is installed and configured.",
        "why": "Detects committed secrets before they leave the developer machine.",
        "applies_to": ["any"],
        "install": {
            "macos": "brew install gitleaks",
            "linux": "apt install gitleaks || nix-shell -p gitleaks",
        },
    }
    result = validate_prescribed(data)
    assert result.install["macos"] == "brew install gitleaks"


def test_prescribed_missing_required_field_raises():
    """Missing a required field raises ValueError with the field name."""
    data = {"id": "x", "version": 1, "what": "x", "why": "x"}  # missing applies_to
    with pytest.raises(ValueError, match="applies_to"):
        validate_prescribed(data)


def test_prescribed_id_format():
    """id must be dot-delimited: profile.domain.control-name."""
    data = {
        "id": "invalid_no_dots",
        "version": 1,
        "what": "x",
        "why": "x",
        "applies_to": ["any"],
    }
    with pytest.raises(ValueError, match="id format"):
        validate_prescribed(data)
