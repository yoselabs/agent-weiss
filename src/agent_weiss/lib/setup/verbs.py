"""Parse user-typed setup verbs into a Decision.

Grammar (case-insensitive on verb keywords):
    "approve all"              -> approve_all=True
    "approve <domain>"         -> approve_domains=[domain]
    "<numbers>"                -> approve_indices=[...]
    "skip <numbers>[: reason]" -> skip_indices=[...] (+ skip_reasons)
    "explain <N>"              -> explain_index=N
    "dry-run"                  -> dry_run=True
    "cancel"                   -> cancel=True

Numbers may be space- or comma-separated. Indices are 1-based and validated
against num_proposals. Domain names validated against available_domains.
"""
from __future__ import annotations
import re

from agent_weiss.lib.setup.types import Decision


class VerbParseError(ValueError):
    """User-typed verb couldn't be parsed."""


_NUMBERS_RE = re.compile(r"[\s,]+")


def parse_verb(
    user_input: str,
    *,
    num_proposals: int,
    available_domains: list[str],
) -> Decision:
    """Parse user_input into a Decision. Raise VerbParseError on syntax issues."""
    text = user_input.strip()
    if not text:
        raise VerbParseError("empty input")

    lowered = text.lower()

    if lowered == "cancel":
        return Decision(cancel=True)
    if lowered == "dry-run":
        return Decision(dry_run=True)
    if lowered == "approve all":
        return Decision(approve_all=True)

    if lowered.startswith("approve "):
        rest = text[len("approve "):].strip()
        if rest.lower() not in [d.lower() for d in available_domains]:
            raise VerbParseError(
                f"unknown domain {rest!r} (available: {available_domains})"
            )
        # Match the original casing from available_domains
        canonical = next(d for d in available_domains if d.lower() == rest.lower())
        return Decision(approve_domains=[canonical])

    if lowered.startswith("explain "):
        rest = text[len("explain "):].strip()
        try:
            n = int(rest)
        except ValueError as e:
            raise VerbParseError(f"explain expects a number, got {rest!r}") from e
        if not (1 <= n <= num_proposals):
            raise VerbParseError(
                f"explain index {n} out of range (1..{num_proposals})"
            )
        return Decision(explain_index=n)

    if lowered.startswith("skip "):
        rest = text[len("skip "):].strip()
        nums_part, reason = _split_reason(rest)
        indices = _parse_numbers(nums_part, num_proposals)
        skip_reasons = {i: reason for i in indices} if reason else {}
        return Decision(skip_indices=indices, skip_reasons=skip_reasons)

    # Bare numbers (with optional commas) - approve those indices.
    if re.fullmatch(r"[0-9, ]+", text):
        indices = _parse_numbers(text, num_proposals)
        return Decision(approve_indices=indices)

    raise VerbParseError(f"unknown verb in {user_input!r}")


def _split_reason(text: str) -> tuple[str, str | None]:
    """Split 'numbers: reason' into ('numbers', 'reason') or ('numbers', None)."""
    if ":" in text:
        nums, reason = text.split(":", 1)
        return nums.strip(), reason.strip()
    return text, None


def _parse_numbers(text: str, num_proposals: int) -> list[int]:
    """Parse space- or comma-separated numbers; validate range."""
    text = text.strip()
    if not text:
        raise VerbParseError("expected one or more numbers")
    parts = [p for p in _NUMBERS_RE.split(text) if p]
    out: list[int] = []
    for p in parts:
        try:
            n = int(p)
        except ValueError as e:
            raise VerbParseError(f"not a number: {p!r}") from e
        if not (1 <= n <= num_proposals):
            raise VerbParseError(
                f"index {n} out of range (1..{num_proposals})"
            )
        out.append(n)
    return out
