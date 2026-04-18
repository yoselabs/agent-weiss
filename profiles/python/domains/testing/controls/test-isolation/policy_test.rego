package python.testing.test_isolation_test

import rego.v1
import data.python.testing.test_isolation

test_missing_env_fires if {
	test_isolation.deny with input as {"tool": {"pytest": {"ini_options": {"addopts": "-v"}}}}
}

test_with_env_passes if {
	count(test_isolation.deny) == 0 with input as {"tool": {"pytest": {"ini_options": {
		"addopts": "-v",
		"env": ["DATABASE_URL=postgresql://localhost:5433/test_db"],
	}}}}
}
