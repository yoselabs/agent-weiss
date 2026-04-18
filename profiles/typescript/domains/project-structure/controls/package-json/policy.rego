package typescript.project_structure.package_json

# WHAT: Ensures package.json has engines, type:"module", and no wildcard versions.
# WHY: see instruct.md.
# Input: parsed package.json (JSON)

import rego.v1

# ── Policy: engines field must exist ──

deny contains msg if {
	not input.engines
	msg := "package.json: missing 'engines' field — specify Node version to prevent version mismatch"
}

# ── Policy: type must be "module" ──
# Source policy used `warn`; converted to `deny` because agent-weiss contract
# has no warn level (and modern TS projects should be ESM by default).

deny contains msg if {
	not input.type
	msg := "package.json: missing 'type' field — set '\"type\": \"module\"' for explicit ESM"
}

deny contains msg if {
	input.type
	input.type != "module"
	msg := sprintf("package.json: 'type' is '%s' — should be 'module' for ESM consistency", [input.type])
}

# ── Policy: no wildcard versions in dependencies ──

deny contains msg if {
	some dep, version in input.dependencies
	version == "*"
	msg := sprintf("package.json: dependency '%s' has wildcard version '*' — pin to explicit range", [dep])
}

deny contains msg if {
	some dep, version in input.devDependencies
	version == "*"
	msg := sprintf("package.json: devDependency '%s' has wildcard version '*' — pin to explicit range", [dep])
}
