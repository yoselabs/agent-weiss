"""Resolve the agent-weiss bundle root.

Order:
1. AGENT_WEISS_BUNDLE env var (set by installers, manual override)
2. Probe known install locations (Claude → PyPI → npm)
"""
from __future__ import annotations
import os
import sys
from pathlib import Path


class BundleNotFoundError(RuntimeError):
    """Raised when no agent-weiss bundle can be located."""


def _default_probe_paths() -> list[Path]:
    """Default candidate paths for the bundle, in priority order.

    Claude Code marketplace install → PyPI install → npm install.
    """
    home = Path.home()
    paths: list[Path] = []

    # Claude Code marketplace
    paths.append(home / ".claude" / "plugins" / "yoselabs" / "agent-weiss")

    # PyPI install — share dir of the active Python prefix
    paths.append(Path(sys.prefix) / "share" / "agent-weiss")

    # npm install — common npm prefixes
    for npm_prefix in (
        Path("/usr/local"),
        home / ".local",
        home / ".npm-global",
    ):
        paths.append(npm_prefix / "share" / "agent-weiss")

    return paths


def resolve_bundle_root(probe_paths: list[Path] | None = None) -> Path:
    """Resolve the bundle root directory.

    Returns the first directory containing a bundle.yaml.
    Raises BundleNotFoundError if none found.
    """
    env = os.environ.get("AGENT_WEISS_BUNDLE")
    if env:
        candidate = Path(env)
        if (candidate / "bundle.yaml").exists():
            return candidate
        raise BundleNotFoundError(
            f"AGENT_WEISS_BUNDLE points to {candidate} but no bundle.yaml found there."
        )

    candidates = probe_paths if probe_paths is not None else _default_probe_paths()
    for c in candidates:
        if (c / "bundle.yaml").exists():
            return c

    raise BundleNotFoundError(
        "No agent-weiss bundle found. Set AGENT_WEISS_BUNDLE or install via "
        "Claude marketplace, PyPI, or npm."
    )
