"""Tests for reconcile rendering (batching pattern matches setup)."""
from agent_weiss.lib.reconcile import Anomaly, ReconcileReport, render_anomalies


def test_render_empty_report():
    text = render_anomalies(ReconcileReport())
    assert text.strip()
    assert "no anomalies" in text.lower() or "nothing" in text.lower()


def test_render_groups_by_kind():
    report = ReconcileReport(anomalies=[
        Anomaly(kind="orphan", path=".agent-weiss/policies/a.rego", detail="x"),
        Anomaly(kind="ghost", path=".agent-weiss/policies/b.rego", detail="y"),
        Anomaly(kind="orphan", path=".agent-weiss/policies/c.rego", detail="z"),
    ])
    text = render_anomalies(report)
    orphan_pos = text.lower().index("orphan")
    ghost_pos = text.lower().index("ghost")
    a_pos = text.index("a.rego")
    b_pos = text.index("b.rego")
    c_pos = text.index("c.rego")
    # orphans listed before ghosts (first-seen order)
    assert orphan_pos < ghost_pos
    # both orphans under the orphan header
    assert a_pos < ghost_pos
    assert c_pos < ghost_pos


def test_render_numbers_globally():
    report = ReconcileReport(anomalies=[
        Anomaly(kind="orphan", path="a", detail="x"),
        Anomaly(kind="ghost", path="b", detail="y"),
        Anomaly(kind="locally_modified", path="c", detail="z"),
    ])
    text = render_anomalies(report)
    assert "1." in text
    assert "2." in text
    assert "3." in text
