"""Setup workflow orchestration helpers.

The skill.md scaffold from Plan 1 invokes these helpers in sequence:
1. compute_proposals — gap-analyze each control, return Proposals
2. batch_by_domain — group proposals by domain for the user prompt
3. parse_verb — turn user input into a Decision
4. apply_proposal — execute approved actions (manual_action: record handled;
   install_file/merge_fragment: stubs for v2)
5. write_dry_run_report — generate the dry-run markdown
"""
