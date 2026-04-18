package python.testing.coverage_config

# WHAT: Ensures [tool.coverage] is configured for agent-readable output.
# WHY: see instruct.md.
# Input: parsed pyproject.toml (TOML -> JSON via conftest)

import rego.v1

# ── Policy: skip_covered = true ──

deny contains msg if {
	report := input.tool.coverage.report
	not report.skip_covered
	msg := "coverage.report: missing 'skip_covered' — set to true so agents only see files with gaps"
}

deny contains msg if {
	report := input.tool.coverage.report
	report.skip_covered == false
	msg := "coverage.report: skip_covered is false — set to true so agents only see files with gaps"
}

# ── Policy: branch coverage enabled ──

deny contains msg if {
	run := input.tool.coverage.run
	not run.branch
	msg := "coverage.run: missing 'branch' — set to true to catch untested if/else branches"
}

deny contains msg if {
	run := input.tool.coverage.run
	run.branch == false
	msg := "coverage.run: branch is false — set to true to catch untested if/else branches"
}
