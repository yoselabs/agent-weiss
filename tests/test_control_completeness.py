"""Self-test: every control directory has the required artifacts.

Required: prescribed.yaml, instruct.md.
Required for non-judgment-only controls: check.sh.
Required for fixture-tested controls: pass/ and fail/ fixtures.

Validation also runs prescribed.yaml through the schema validator.
"""
from __future__ import annotations
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from agent_weiss.lib.schemas import validate_prescribed


REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES = REPO_ROOT / "profiles"
FIXTURES = REPO_ROOT / "fixtures"


def _all_control_dirs() -> list[Path]:
    """Every directory under profiles/*/domains/*/controls/*/."""
    out: list[Path] = []
    for control_dir in PROFILES.rglob("controls/*"):
        if control_dir.is_dir():
            out.append(control_dir)
    return out


@pytest.mark.parametrize("control_dir", _all_control_dirs(), ids=lambda p: str(p.relative_to(PROFILES)))
def test_control_has_prescribed_yaml(control_dir: Path):
    p = control_dir / "prescribed.yaml"
    assert p.exists(), f"{control_dir} missing prescribed.yaml"
    yaml = YAML(typ="safe")
    data = yaml.load(p)
    assert data is not None, f"{p} is empty"
    validate_prescribed(data)  # raises on schema violation


@pytest.mark.parametrize("control_dir", _all_control_dirs(), ids=lambda p: str(p.relative_to(PROFILES)))
def test_control_has_instruct_md(control_dir: Path):
    p = control_dir / "instruct.md"
    assert p.exists(), f"{control_dir} missing instruct.md"
    assert p.read_text().strip(), f"{p} is empty"


@pytest.mark.parametrize("control_dir", _all_control_dirs(), ids=lambda p: str(p.relative_to(PROFILES)))
def test_control_has_fixtures(control_dir: Path):
    """Every control should have pass/ and fail/ fixtures.

    Fixture layout mirrors profiles under fixtures/profiles/<rest>.
    """
    relative = control_dir.relative_to(PROFILES)
    fixture_dir = FIXTURES / "profiles" / relative
    assert (fixture_dir / "pass").is_dir(), f"missing pass fixture at {fixture_dir / 'pass'}"
    assert (fixture_dir / "fail").is_dir(), f"missing fail fixture at {fixture_dir / 'fail'}"


@pytest.mark.parametrize("control_dir", _all_control_dirs(), ids=lambda p: str(p.relative_to(PROFILES)))
def test_control_id_matches_path(control_dir: Path):
    """prescribed.yaml id must match the directory path: profile.domain.control."""
    p = control_dir / "prescribed.yaml"
    yaml = YAML(typ="safe")
    data = yaml.load(p)
    relative = control_dir.relative_to(PROFILES)
    parts = relative.parts  # ('profile', 'domains', 'domain', 'controls', 'control')
    expected_id = f"{parts[0]}.{parts[2]}.{parts[4]}"
    assert data["id"] == expected_id, (
        f"prescribed.yaml id={data['id']!r} doesn't match path-derived id={expected_id!r}"
    )
