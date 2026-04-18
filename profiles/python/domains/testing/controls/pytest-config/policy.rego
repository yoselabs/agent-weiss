package python.testing.pytest_config

# WHAT: Ensures pytest is configured with strict markers, coverage, and a
# meaningful coverage threshold.
# WHY: see instruct.md.
# Input: parsed pyproject.toml (TOML -> JSON via conftest)

import rego.v1

# ── deny: strict-markers must be enabled ──

deny contains msg if {
	opts := input.tool.pytest.ini_options
	addopts := opts.addopts
	not contains(addopts, "--strict-markers")
	msg := "pytest: addopts missing '--strict-markers' — catches marker typos deterministically"
}

# ── deny: coverage must be enabled ──

deny contains msg if {
	opts := input.tool.pytest.ini_options
	addopts := opts.addopts
	not contains(addopts, "--cov")
	msg := "pytest: addopts missing '--cov' — coverage should run with every test invocation"
}

# ── deny: coverage threshold must exist ──

deny contains msg if {
	opts := input.tool.pytest.ini_options
	addopts := opts.addopts
	not contains(addopts, "--cov-fail-under")
	msg := "pytest: addopts missing '--cov-fail-under' — set a coverage threshold (recommended: 95)"
}

# ── deny: coverage threshold must not be absurdly low ──

deny contains msg if {
	opts := input.tool.pytest.ini_options
	addopts := opts.addopts
	contains(addopts, "--cov-fail-under")
	parts := split(addopts, "--cov-fail-under=")
	count(parts) > 1
	threshold_str := split(parts[1], " ")[0]
	threshold := to_number(threshold_str)
	threshold < 30
	msg := sprintf("pytest: --cov-fail-under=%v is below 30%% — this gate catches nothing meaningful", [threshold])
}
