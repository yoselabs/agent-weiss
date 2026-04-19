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

Detect drift between `.agent-weiss.yaml` state and the project's working tree.
The reconciliation detector is non-destructive — it only reports anomalies.

```python
from pathlib import Path
from agent_weiss.lib.reconcile import reconcile, render_anomalies

report = reconcile(Path("<project_root>"))
print(render_anomalies(report))
```

If `report.anomalies` is non-empty, prompt the user with the rendered text
followed by:

> "Resolve these anomalies — verbs: `<numbers>` to mark resolved, `skip <numbers>: <reason>` to override, `cancel`. Or describe a different action you'd like me to take."

Parse user input with `agent_weiss.lib.setup.verbs.parse_verb` (same parser
as the Setup phase). Apply per-anomaly resolutions to state — for orphans,
either re-track them in `prescribed_files` or delete them; for ghosts, either
restore from bundle or remove from `prescribed_files`; for locally_modified,
either accept the local version (re-hash) or restore from bundle.

> Plan 3 limitation: Reconciliation is detection + rendering. Per-anomaly
> apply logic (re-track / restore / accept) is handled by you, the skill —
> follow the user's choice and write the resulting state via `write_state`.

### 3. Confirm profiles

Tell the user: "I detected python + docker. Add or remove any?" Honor their
answer. Persist confirmed profiles in `.agent-weiss.yaml`.

### 4. Setup phase

Compute proposals, batch by domain, render to the user, parse their verb,
cascade dependencies, and apply.

```python
from pathlib import Path
from datetime import datetime
from agent_weiss.lib.state import read_state, write_state
from agent_weiss.lib.bundle import resolve_bundle_root
from agent_weiss.lib.setup.gap import compute_proposals
from agent_weiss.lib.setup.batch import render_proposals
from agent_weiss.lib.setup.verbs import parse_verb, VerbParseError
from agent_weiss.lib.setup.cascade import cascade_skips
from agent_weiss.lib.setup.apply import apply_proposal, ApplyOutcome
from agent_weiss.lib.setup.dry_run import write_dry_run_report

project_root = Path("<project_root>")
state = read_state(project_root)
bundle = resolve_bundle_root()

proposals = compute_proposals(
    project_root=project_root,
    bundle_root=bundle,
    state=state,
)
prompt_text = render_proposals(proposals)
domains = sorted({p.domain for p in proposals})
```

Show `prompt_text` to the user. Then prompt:

> "Which to approve? Verbs: `approve all`, `approve <domain>`, `<numbers>`,
> `skip <numbers>[: reason]`, `explain <N>`, `dry-run`, `cancel`."

Loop:

```python
while True:
    user_input = read_user_input()  # the skill — your job
    try:
        decision = parse_verb(
            user_input,
            num_proposals=len(proposals),
            available_domains=domains,
        )
    except VerbParseError as e:
        show_error_and_reprompt(e)
        continue

    if decision.cancel:
        return  # abort the loop

    if decision.dry_run:
        ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        report_path = write_dry_run_report(
            project_root=project_root,
            proposals=proposals,
            timestamp=ts,
        )
        print(f"Dry-run report written to {report_path}. Exiting.")
        return

    if decision.explain_index is not None:
        show_instruct_md(proposals[decision.explain_index - 1])
        continue  # re-prompt

    break

# Cascade skips for declined dependencies
decision = cascade_skips(proposals=proposals, decision=decision)

# Apply each proposal's outcome.
decided_at = datetime.now().date().isoformat()
for i, p in enumerate(proposals, start=1):
    if decision.approve_all or i in decision.approve_indices or p.domain in decision.approve_domains:
        outcome = ApplyOutcome.APPROVED
        reason = None
    elif i in decision.skip_indices:
        outcome = ApplyOutcome.SKIPPED
        reason = decision.skip_reasons.get(i)
    else:
        # Neither approved nor skipped — treat as deferred (no state change).
        continue

    state, _ = apply_proposal(
        proposal=p,
        state=state,
        outcome=outcome,
        decided_at=decided_at,
        reason=reason,
    )

write_state(project_root, state)
```

For each MANUAL_ACTION proposal that was approved, you (the skill) must show
the user the contents of `proposal.instruct_path` so they can carry out the
action manually. Confirm with them ("done?") before recording approval.

For approved proposals where the user confirmed handled, the next Verify run
(step 5) checks that the action stuck. For declined proposals with a reason,
the override is recorded and counts as 'pass' in the Setup score (Plan 4).

> Plan 3 limitation: only MANUAL_ACTION proposals are supported. INSTALL_FILE
> and MERGE_FRAGMENT raise NotImplementedError until later plans add file
> install + config-merge logic.

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
