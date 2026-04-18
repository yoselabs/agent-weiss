package python.testing.coverage_config_test

import rego.v1
import data.python.testing.coverage_config

test_missing_skip_covered_fires if {
	coverage_config.deny with input as {"tool": {"coverage": {
		"report": {},
		"run": {"branch": true},
	}}}
}

test_skip_covered_false_fires if {
	coverage_config.deny with input as {"tool": {"coverage": {
		"report": {"skip_covered": false},
		"run": {"branch": true},
	}}}
}

test_missing_branch_fires if {
	coverage_config.deny with input as {"tool": {"coverage": {
		"report": {"skip_covered": true},
		"run": {},
	}}}
}

test_branch_false_fires if {
	coverage_config.deny with input as {"tool": {"coverage": {
		"report": {"skip_covered": true},
		"run": {"branch": false},
	}}}
}

test_good_config_passes if {
	count(coverage_config.deny) == 0 with input as {"tool": {"coverage": {
		"report": {"skip_covered": true},
		"run": {"branch": true},
	}}}
}
