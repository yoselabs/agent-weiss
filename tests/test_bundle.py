"""Tests for bundle root resolution."""
from pathlib import Path
import pytest
from agent_weiss.lib.bundle import resolve_bundle_root, BundleNotFoundError


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch):
    """Always start each test with AGENT_WEISS_BUNDLE unset, so external env doesn't leak in."""
    monkeypatch.delenv("AGENT_WEISS_BUNDLE", raising=False)


def test_resolve_via_env_var(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """AGENT_WEISS_BUNDLE env var takes precedence over probe order."""
    bundle = tmp_path / "my-bundle"
    bundle.mkdir()
    (bundle / "bundle.yaml").write_text("version: '0.0.1'\nfiles: {}\n")

    monkeypatch.setenv("AGENT_WEISS_BUNDLE", str(bundle))
    assert resolve_bundle_root() == bundle


def test_env_var_pointing_to_invalid_dir_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """If env var points somewhere without bundle.yaml, raise."""
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv("AGENT_WEISS_BUNDLE", str(empty))
    with pytest.raises(BundleNotFoundError, match="bundle.yaml"):
        resolve_bundle_root()


def test_resolve_via_probe(tmp_path: Path):
    """With env var unset, probe walks the candidate paths in order."""
    candidate = tmp_path / "fake-claude-plugins" / "yoselabs" / "agent-weiss"
    candidate.mkdir(parents=True)
    (candidate / "bundle.yaml").write_text("version: '0.0.1'\nfiles: {}\n")

    assert resolve_bundle_root(probe_paths=[candidate]) == candidate


def test_no_bundle_anywhere_raises():
    """If env var unset and probe finds nothing, raise."""
    with pytest.raises(BundleNotFoundError):
        resolve_bundle_root(probe_paths=[Path("/nonexistent/a"), Path("/nonexistent/b")])
