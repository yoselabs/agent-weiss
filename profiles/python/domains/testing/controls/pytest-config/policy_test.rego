package python.testing.pytest_config_test

import rego.v1
import data.python.testing.pytest_config

test_missing_strict_markers_fires if {
	pytest_config.deny with input as {"tool": {"pytest": {"ini_options": {"addopts": "-v --cov --cov-fail-under=95"}}}}
}

test_missing_cov_fires if {
	pytest_config.deny with input as {"tool": {"pytest": {"ini_options": {"addopts": "-v --strict-markers --cov-fail-under=95"}}}}
}

test_missing_cov_fail_under_fires if {
	pytest_config.deny with input as {"tool": {"pytest": {"ini_options": {"addopts": "-v --strict-markers --cov"}}}}
}

test_threshold_below_30_fires if {
	pytest_config.deny with input as {"tool": {"pytest": {"ini_options": {"addopts": "-v --strict-markers --cov --cov-fail-under=15"}}}}
}

test_threshold_at_30_passes if {
	count(pytest_config.deny) == 0 with input as {"tool": {"pytest": {"ini_options": {"addopts": "-v --strict-markers --cov --cov-fail-under=30"}}}}
}

test_good_config_passes if {
	count(pytest_config.deny) == 0 with input as {"tool": {"pytest": {"ini_options": {"addopts": "-v --strict-markers --cov --cov-fail-under=95"}}}}
}
