"""Schema validation for prescribed.yaml and bundle.yaml.

Schemas are simple dataclasses validated by hand. This avoids a heavy
schema library dependency and keeps the surface readable for contributors.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any

ID_PATTERN = re.compile(r"^[a-z0-9-]+\.[a-z0-9-]+\.[a-z0-9-]+$")


@dataclass(frozen=True)
class PrescribedSchema:
    """A single control's prescribed configuration.

    Required fields: id, version, what, why, applies_to.
    Optional: install (per-OS shell command), config_fragment, depends_on.
    """
    id: str
    version: int
    what: str
    why: str
    applies_to: list[str]
    install: dict[str, str] = field(default_factory=dict)
    config_fragment: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)


# applies_to vocabulary (v1):
# - "any" — applies to any project regardless of stack
# - "<profile_id>" — applies when this profile matches (e.g., "python", "typescript", "docker")
# - The list is OR-ed: `["python", "typescript"]` means applies if either profile matches.
# Validation does NOT enforce vocabulary in v1 (free-form strings); profile matchers in
# Plan 3+4 will define which strings are recognized. Keep entries lowercase, hyphenated.


_REQUIRED_FIELDS = ("id", "version", "what", "why", "applies_to")


def validate_prescribed(data: dict[str, Any]) -> PrescribedSchema:
    """Validate a prescribed.yaml dict and return a PrescribedSchema.

    Raises ValueError on missing required fields or invalid id format.
    """
    for field_name in _REQUIRED_FIELDS:
        if field_name not in data:
            raise ValueError(f"prescribed.yaml missing required field: {field_name}")

    if not ID_PATTERN.match(data["id"]):
        raise ValueError(
            f"id format invalid: {data['id']!r}. Expected: profile.domain.control-name"
        )

    return PrescribedSchema(
        id=data["id"],
        version=int(data["version"]),
        what=data["what"],
        why=data["why"],
        applies_to=list(data["applies_to"]),
        install=dict(data.get("install", {})),
        config_fragment=dict(data.get("config_fragment", {})),
        depends_on=list(data.get("depends_on", [])),
    )


@dataclass(frozen=True)
class BundleSchema:
    """The bundle's manifest, located at <bundle_root>/bundle.yaml.

    files: mapping of bundle-relative path → sha256 hex digest.
    Used for drift detection (compare project's recorded hash against current bundle's).
    """
    version: str
    files: dict[str, str]

    def hash_for(self, path: str) -> str | None:
        """Return the recorded sha256 for a bundle-relative path, or None if missing."""
        return self.files.get(path)


def validate_bundle(data: dict[str, Any]) -> BundleSchema:
    """Validate a bundle.yaml dict and return a BundleSchema.

    Raises ValueError on missing/malformed fields.
    """
    if "version" not in data:
        raise ValueError("bundle.yaml missing required field: version")
    if "files" not in data:
        raise ValueError("bundle.yaml missing required field: files")
    if not isinstance(data["files"], dict):
        raise ValueError("bundle.yaml files must be a mapping (path → sha256)")

    return BundleSchema(
        version=str(data["version"]),
        files={str(k): str(v) for k, v in data["files"].items()},
    )
