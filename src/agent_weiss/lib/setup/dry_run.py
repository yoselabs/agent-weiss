"""Generate a markdown report for `dry-run` mode.

The report lists every proposal grouped by domain so the user can review
without committing to any changes.
"""
from __future__ import annotations
from pathlib import Path

from agent_weiss.lib.setup.types import Proposal
from agent_weiss.lib.setup.batch import batch_by_domain


DRY_RUN_DIR = ".agent-weiss"


def write_dry_run_report(
    *,
    project_root: Path,
    proposals: list[Proposal],
    timestamp: str,
) -> Path:
    """Write the dry-run report and return its path."""
    report_dir = project_root / DRY_RUN_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"dry-run-{timestamp}.md"

    lines: list[str] = [f"# agent-weiss dry-run report ({timestamp})", ""]

    if not proposals:
        lines.append("No proposals — every applicable control is satisfied or overridden.")
        path.write_text("\n".join(lines) + "\n")
        return path

    lines.append(f"{len(proposals)} proposed action(s) across {len(set(p.domain for p in proposals))} domain(s).")
    lines.append("")

    batched = batch_by_domain(proposals)
    counter = 1
    for domain, items in batched.items():
        lines.append(f"## {domain}")
        lines.append("")
        for p in items:
            lines.append(f"### {counter}. {p.control_id}")
            lines.append("")
            lines.append(f"**Action:** {p.action_kind.value}")
            lines.append(f"**Summary:** {p.summary}")
            if p.depends_on:
                lines.append(f"**Depends on:** {', '.join(p.depends_on)}")
            if p.instruct_path is not None:
                # Render the instruct path relative to project_root if possible, else just name.
                try:
                    rel = p.instruct_path.relative_to(project_root)
                    lines.append(f"**Details:** see `{rel}`")
                except ValueError:
                    lines.append(f"**Details:** see `{p.instruct_path.name}`")
            lines.append("")
            counter += 1

    path.write_text("\n".join(lines).rstrip() + "\n")
    return path
