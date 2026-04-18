package python.quality.ruff_config_test

import rego.v1
import data.python.quality.ruff_config

test_missing_output_format_fires if {
	ruff_config.deny with input as {"tool": {"ruff": {"line-length": 140, "lint": {"mccabe": {"max-complexity": 10}}}}}
}

test_wrong_output_format_fires if {
	ruff_config.deny with input as {"tool": {"ruff": {"output-format": "full", "line-length": 140, "lint": {"mccabe": {"max-complexity": 10}}}}}
}

test_missing_line_length_fires if {
	ruff_config.deny with input as {"tool": {"ruff": {"output-format": "concise", "lint": {"mccabe": {"max-complexity": 10}}}}}
}

test_short_line_length_fires if {
	ruff_config.deny with input as {"tool": {"ruff": {"output-format": "concise", "line-length": 80, "lint": {"mccabe": {"max-complexity": 10}}}}}
}

test_missing_complexity_fires if {
	ruff_config.deny with input as {"tool": {"ruff": {"output-format": "concise", "line-length": 140, "lint": {}}}}
}

test_high_complexity_fires if {
	ruff_config.deny with input as {"tool": {"ruff": {"output-format": "concise", "line-length": 140, "lint": {"mccabe": {"max-complexity": 20}}}}}
}

test_good_config_passes if {
	count(ruff_config.deny) == 0 with input as {"tool": {"ruff": {"output-format": "concise", "line-length": 140, "lint": {"mccabe": {"max-complexity": 10}}}}}
}
