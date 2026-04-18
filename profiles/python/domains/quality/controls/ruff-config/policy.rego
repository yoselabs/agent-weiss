package python.quality.ruff_config

# WHAT: Enforces critical ruff settings: concise output, adequate line length,
# and complexity limits.
# WHY: see instruct.md.
# Input: parsed pyproject.toml (TOML -> JSON via conftest)

import rego.v1

# ── Policy: output-format must be "concise" ──

deny contains msg if {
	ruff := input.tool.ruff
	not ruff["output-format"]
	msg := "ruff: missing 'output-format' — set to \"concise\" for agent-readable one-line errors"
}

deny contains msg if {
	ruff := input.tool.ruff
	ruff["output-format"] != "concise"
	msg := sprintf("ruff: output-format is \"%s\" — should be \"concise\" for agent-readable one-line errors", [ruff["output-format"]])
}

# ── Policy: line-length >= 120 ──

deny contains msg if {
	ruff := input.tool.ruff
	not ruff["line-length"]
	msg := "ruff: missing 'line-length' — set to 120 to reduce unnecessary wrapping noise"
}

deny contains msg if {
	ruff := input.tool.ruff
	ruff["line-length"] < 120
	msg := sprintf("ruff: line-length is %d — should be >= 120 to reduce unnecessary wrapping noise for agents", [ruff["line-length"]])
}

# ── Policy: complexity limits set ──

deny contains msg if {
	ruff := input.tool.ruff
	not ruff.lint.mccabe["max-complexity"]
	msg := "ruff: missing mccabe max-complexity — set to 10 to prevent agents from generating sprawling functions"
}

deny contains msg if {
	ruff := input.tool.ruff
	ruff.lint.mccabe["max-complexity"] > 15
	msg := sprintf("ruff: mccabe max-complexity is %d — should be <= 15 (recommended: 10)", [ruff.lint.mccabe["max-complexity"]])
}
