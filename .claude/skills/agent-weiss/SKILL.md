---
name: agent-weiss
description: |
  Audits and sets up codebases to be agent-ready. Detects the project's stack,
  matches applicable profiles, gap-analyzes against prescribed standards, applies
  approved changes, and produces Setup + Quality scores. Run this whenever you
  want to confirm a project is configured well for AI coding agents.
---

# agent-weiss

You are running the **agent-weiss skill**: a knowledge companion that audits
codebases for agent-readiness and sets up missing infrastructure with explicit
user approval.

## Bundle root

The agent-weiss bundle (profiles, controls, helper scripts) is resolved via:

1. `$AGENT_WEISS_BUNDLE` env var (manual override)
2. `~/.claude/plugins/yoselabs/agent-weiss/` (Claude marketplace install)
3. `<python-prefix>/share/agent-weiss/` (PyPI install)
4. `<npm-prefix>/share/agent-weiss/` (npm install)

When in doubt, the bundle resolver can be invoked directly:

```python
from agent_weiss.lib.bundle import resolve_bundle_root
print(resolve_bundle_root())
```

This prints the resolved root or raises `BundleNotFoundError`.

## Standard run loop

Follow these steps every time the user invokes the skill. Do not skip steps.

### 1. Detect

Read `<project_root>/.agent-weiss.yaml` if it exists. Note the `bundle_version`,
`profiles`, and `prescribed_files` map. If absent, treat this as a first run.

Scan the project root for stack signals:
- `pyproject.toml` → python profile candidate
- `package.json` → typescript profile candidate
- `Dockerfile` → docker profile candidate (deferred to v2; surface as detected
  but not yet supported)

### 2. Reconcile

Invoke the reconciliation detector:

```python
from pathlib import Path
from agent_weiss.lib.reconcile import reconcile
report = reconcile(Path("<project_root>"))
for anomaly in report.anomalies:
    # surface to user
    ...
```

> Plan 1 limitation: orphan detection only scans `.agent-weiss/policies/`. Files prescribed at other paths (e.g., `.pre-commit-config.yaml`) get ghost detection but not orphan detection. Plan 3 will broaden this.

For each anomaly returned (orphan / ghost / locally_modified), prompt the user
with the appropriate choice set per spec §6 "Reconciliation." Do not silently
delete or reclassify files.

### 3. Confirm profiles

Tell the user: "I detected python + docker. Add or remove any?" Honor their
answer. Persist confirmed profiles in `.agent-weiss.yaml`.

### 4. Setup phase

For each control in each confirmed profile, gap-analyze: is the prescribed
state present? If not, propose the change.

Show the user the full setup plan, batched by domain. Use the verbs:
`approve all`, `approve <domain>`, `<numbers>`, `skip <numbers>`,
`explain <N>`, `dry-run`, `cancel`. Apply approved changes, backing up any
overwritten file to `.agent-weiss/backups/<timestamp>/`.

### 5. Verify phase

For each control, run its `check.sh`. Parse the JSON output line per the
contract:
- `status: pass` (exit 0) — control satisfied
- `status: fail` (exit 1) — Quality issue, surface findings_count and summary
- `status: setup-unmet` (exit 127) — control infrastructure missing, surface
  the install command and treat as Setup-unmet

### 6. Score and report

Compute per spec §7:
- Setup score: per-control 100/0, per-domain average, total average of domains.
  Override-with-reason counts as 100.
- Quality score: per-control 100/0, exclude setup-unmet controls.

Print the report in the format shown in spec §7.

### 7. Update state

Write the updated `.agent-weiss.yaml` with: confirmed profiles, prescribed_files
map (with fresh sha256 hashes for any files copied this run), scores, drift,
last_scan / last_setup timestamps.

## What you must NEVER do

- Auto-install tools (`brew`, `uv`, `pnpm`, `apt`). Always instruct the user.
- Silently overwrite files. Always back up first.
- Treat header comments as load-bearing. State file is source of truth.
- Skip the reconciliation step. It must run before setup phase.

## Cross-references

- Spec: `docs/spec.md`
- Helper modules: `src/agent_weiss/lib/`
- Profiles: `profiles/`
- Fixtures (for skill self-tests, not for users): `fixtures/`
