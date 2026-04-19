"""Format the verify-phase report as markdown.

Layout:
    # agent-weiss verify report

    **Setup:** 87% (per-domain: docs 100%, security 67%)
    **Quality:** 92% (per-domain: docs 100%, security 50%)

    ## docs
    - ✓ universal.docs.agents-md-present — AGENTS.md present
    - ✓ universal.docs.claude-md-present — CLAUDE.md present
    - ✗ universal.docs.readme-present — fail: no README.* found

    ## security
    - ⚠ universal.security.gitignore-secrets — setup-unmet: conftest not installed
      Install: brew install conftest
    - ⊘ universal.security.gitleaks-precommit — override: we don't use pre-commit
    ...
"""
from __future__ import annotations
from collections import OrderedDict

from agent_weiss.lib.contract import Status
from agent_weiss.lib.setup.types import OverrideEntry
from agent_weiss.lib.verify.types import ControlResult
from agent_weiss.lib.verify.score import ScoreReport


def format_report(
    *,
    results: list[ControlResult],
    setup_score: ScoreReport,
    quality_score: ScoreReport,
    overrides: dict[str, OverrideEntry],
) -> str:
    """Render verify results + scores as a markdown report."""
    lines: list[str] = ["# agent-weiss verify report", ""]

    if not results:
        lines.append("No applicable controls were checked.")
        return "\n".join(lines) + "\n"

    # Overall scores
    lines.append(f"**Setup:** {round(setup_score.total)}%")
    lines.append(f"**Quality:** {round(quality_score.total)}%")
    lines.append("")

    # Per-domain breakdown
    by_domain: OrderedDict[str, list[ControlResult]] = OrderedDict()
    for r in results:
        by_domain.setdefault(r.domain, []).append(r)

    for domain, items in by_domain.items():
        lines.append(f"## {domain}")
        for r in items:
            marker, descriptor = _marker_and_descriptor(r, overrides)
            lines.append(f"- {marker} {r.control_id} — {descriptor}")
            if r.status is Status.SETUP_UNMET and r.install and r.control_id not in overrides:
                lines.append(f"  Install: {r.install}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _format_per_domain(score: ScoreReport) -> str:
    """Render per-domain scores like 'docs 100%, security 67%'."""
    if not score.per_domain:
        return "(no domains)"
    return ", ".join(
        f"{domain} {round(value)}%" for domain, value in score.per_domain.items()
    )


def _marker_and_descriptor(
    result: ControlResult,
    overrides: dict[str, OverrideEntry],
) -> tuple[str, str]:
    """Return (marker glyph, descriptor) for a control result."""
    if result.control_id in overrides:
        return "⊘", f"override: {overrides[result.control_id].reason}"
    if result.status is Status.PASS:
        return "✓", result.summary
    if result.status is Status.FAIL:
        return "✗", f"fail: {result.summary}"
    # SETUP_UNMET
    return "⚠", f"setup-unmet: {result.summary}"
