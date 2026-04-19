"""Group proposals by domain and render them as numbered prompt text.

Numbering is global (1..N) so the user can type "approve 3 5 7" without
caring about which domain each number belongs to.
"""
from __future__ import annotations
from collections import OrderedDict

from agent_weiss.lib.setup.types import Proposal


def batch_by_domain(proposals: list[Proposal]) -> dict[str, list[Proposal]]:
    """Group proposals by domain, preserving first-seen order of domains."""
    out: OrderedDict[str, list[Proposal]] = OrderedDict()
    for p in proposals:
        out.setdefault(p.domain, []).append(p)
    return dict(out)


def render_proposals(proposals: list[Proposal]) -> str:
    """Render proposals as numbered text, grouped by domain.

    Format:
        ## docs
        1. universal.docs.agents-md-present — Project has AGENTS.md ...
        2. universal.docs.claude-md-present — ...

        ## security
        3. universal.security.gitignore-secrets — ...

    Numbering is global (1..N) across all domains.
    """
    if not proposals:
        return "No setup proposals — every applicable control is satisfied or overridden."

    batched = batch_by_domain(proposals)
    lines: list[str] = []
    counter = 1
    for domain, items in batched.items():
        lines.append(f"## {domain}")
        for p in items:
            lines.append(f"{counter}. {p.control_id} — {p.summary}")
            counter += 1
        lines.append("")  # blank between domains
    return "\n".join(lines).rstrip() + "\n"
