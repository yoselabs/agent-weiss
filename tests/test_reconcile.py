"""Tests for the reconciliation detector."""
from pathlib import Path
from agent_weiss.lib.state import State, PrescribedFileEntry, write_state
from agent_weiss.lib.hashing import sha256_bytes
from agent_weiss.lib.reconcile import reconcile, ReconcileReport, Anomaly


def _setup_project_with_state(tmp_path: Path, prescribed_files: dict[str, PrescribedFileEntry]) -> Path:
    """Helper: create a project root with a state file."""
    state = State(
        bundle_version="0.0.1",
        profiles=["universal"],
        prescribed_files=prescribed_files,
    )
    write_state(tmp_path, state)
    return tmp_path


def test_clean_state_no_anomalies(tmp_path: Path):
    """If state and disk agree, report is empty."""
    policies_dir = tmp_path / ".agent-weiss" / "policies"
    policies_dir.mkdir(parents=True)
    policy = policies_dir / "x.rego"
    policy.write_bytes(b"package x\n")

    _setup_project_with_state(tmp_path, {
        ".agent-weiss/policies/x.rego": PrescribedFileEntry(
            sha256=sha256_bytes(b"package x\n"),
            bundle_path="profiles/universal/domains/docs/controls/x/policy.rego",
            last_synced="2026-04-14",
        ),
    })

    report = reconcile(tmp_path)
    assert isinstance(report, ReconcileReport)
    assert report.anomalies == []


def test_orphan_detected(tmp_path: Path):
    """File present in .agent-weiss/policies but not tracked → orphan."""
    policies_dir = tmp_path / ".agent-weiss" / "policies"
    policies_dir.mkdir(parents=True)
    (policies_dir / "stranger.rego").write_bytes(b"package stranger\n")

    _setup_project_with_state(tmp_path, {})

    report = reconcile(tmp_path)
    assert len(report.anomalies) == 1
    assert report.anomalies[0].kind == "orphan"
    assert report.anomalies[0].path.endswith("stranger.rego")


def test_ghost_detected(tmp_path: Path):
    """Tracked path missing from disk → ghost."""
    _setup_project_with_state(tmp_path, {
        ".agent-weiss/policies/missing.rego": PrescribedFileEntry(
            sha256="abc",
            bundle_path="profiles/x/y/z/policy.rego",
            last_synced="2026-04-14",
        ),
    })

    report = reconcile(tmp_path)
    assert len(report.anomalies) == 1
    assert report.anomalies[0].kind == "ghost"
    assert report.anomalies[0].path == ".agent-weiss/policies/missing.rego"


def test_locally_modified_detected(tmp_path: Path):
    """Tracked path with hash mismatch → locally_modified."""
    policies_dir = tmp_path / ".agent-weiss" / "policies"
    policies_dir.mkdir(parents=True)
    policy = policies_dir / "modded.rego"
    policy.write_bytes(b"package modded_local\n")  # different content

    _setup_project_with_state(tmp_path, {
        ".agent-weiss/policies/modded.rego": PrescribedFileEntry(
            sha256=sha256_bytes(b"package modded_original\n"),
            bundle_path="profiles/x/y/z/policy.rego",
            last_synced="2026-04-14",
        ),
    })

    report = reconcile(tmp_path)
    assert len(report.anomalies) == 1
    assert report.anomalies[0].kind == "locally_modified"
