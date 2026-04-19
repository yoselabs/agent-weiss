"""Verify workflow: run check.sh per control, parse results, score, format.

The skill.md Verify and Score phases call these helpers in sequence:
1. run_all_checks → list[ControlResult]
2. compute_setup_score / compute_quality_score → ScoreReport
3. format_report → markdown string for the user
"""
