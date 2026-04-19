"""Tests for verb parser."""
import pytest
from agent_weiss.lib.setup.verbs import parse_verb, VerbParseError


def test_approve_all():
    d = parse_verb("approve all", num_proposals=10, available_domains=["docs", "security"])
    assert d.approve_all is True
    assert d.approve_indices == []


def test_approve_all_case_insensitive():
    d = parse_verb("Approve All", num_proposals=10, available_domains=["docs"])
    assert d.approve_all is True


def test_approve_domain():
    d = parse_verb("approve docs", num_proposals=10, available_domains=["docs", "security"])
    assert d.approve_domains == ["docs"]
    assert d.approve_all is False


def test_approve_unknown_domain_raises():
    with pytest.raises(VerbParseError, match="domain"):
        parse_verb("approve other", num_proposals=10, available_domains=["docs"])


def test_approve_indices_space_separated():
    d = parse_verb("1 3 5", num_proposals=10, available_domains=["docs"])
    assert d.approve_indices == [1, 3, 5]


def test_approve_indices_comma_separated():
    d = parse_verb("1, 3, 5", num_proposals=10, available_domains=["docs"])
    assert d.approve_indices == [1, 3, 5]


def test_approve_index_out_of_range_raises():
    with pytest.raises(VerbParseError, match="range"):
        parse_verb("99", num_proposals=10, available_domains=["docs"])


def test_skip_indices():
    d = parse_verb("skip 2 4", num_proposals=10, available_domains=["docs"])
    assert d.skip_indices == [2, 4]


def test_skip_with_reason():
    d = parse_verb(
        "skip 2: we use mypy not ty",
        num_proposals=10,
        available_domains=["docs"],
    )
    assert d.skip_indices == [2]
    assert d.skip_reasons[2] == "we use mypy not ty"


def test_skip_multiple_with_reason_applies_to_all():
    d = parse_verb(
        "skip 2 3: legacy project",
        num_proposals=10,
        available_domains=["docs"],
    )
    assert d.skip_indices == [2, 3]
    assert d.skip_reasons[2] == "legacy project"
    assert d.skip_reasons[3] == "legacy project"


def test_explain():
    d = parse_verb("explain 4", num_proposals=10, available_domains=["docs"])
    assert d.explain_index == 4


def test_explain_out_of_range_raises():
    with pytest.raises(VerbParseError, match="range"):
        parse_verb("explain 99", num_proposals=10, available_domains=["docs"])


def test_dry_run():
    d = parse_verb("dry-run", num_proposals=10, available_domains=["docs"])
    assert d.dry_run is True


def test_cancel():
    d = parse_verb("cancel", num_proposals=10, available_domains=["docs"])
    assert d.cancel is True


def test_empty_input_raises():
    with pytest.raises(VerbParseError, match="empty"):
        parse_verb("   ", num_proposals=10, available_domains=["docs"])


def test_unknown_verb_raises():
    with pytest.raises(VerbParseError, match="unknown"):
        parse_verb("teleport 5", num_proposals=10, available_domains=["docs"])
