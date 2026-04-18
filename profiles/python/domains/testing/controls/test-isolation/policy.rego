package python.testing.test_isolation

# WHAT: Ensures pytest-env config injects test environment variables before
# the application reads them.
# WHY: see instruct.md.
# Input: parsed pyproject.toml (TOML -> JSON via conftest)

import rego.v1

# ── Policy: pytest-env configured ──

deny contains msg if {
	opts := input.tool.pytest.ini_options
	not opts.env
	msg := "pytest: no 'env' configuration — add pytest-env entries to isolate tests from production (e.g., test database URL on a separate port)"
}
