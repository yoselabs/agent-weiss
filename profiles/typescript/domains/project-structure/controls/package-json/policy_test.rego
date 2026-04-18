package typescript.project_structure.package_json_test

import rego.v1
import data.typescript.project_structure.package_json

test_missing_engines_denied if {
	count(package_json.deny) > 0 with input as {"name": "x", "version": "1.0.0", "type": "module"}
}

test_engines_present_passes if {
	count(package_json.deny) == 0 with input as {
		"name": "x",
		"engines": {"node": ">=22"},
		"type": "module",
	}
}

test_missing_type_denied if {
	count(package_json.deny) > 0 with input as {
		"name": "x",
		"engines": {"node": ">=22"},
	}
}

test_type_module_no_deny if {
	count(package_json.deny) == 0 with input as {
		"name": "x",
		"engines": {"node": ">=22"},
		"type": "module",
	}
}

test_wildcard_dep_denied if {
	count(package_json.deny) > 0 with input as {
		"name": "x",
		"engines": {"node": ">=22"},
		"type": "module",
		"dependencies": {"bad-pkg": "*"},
	}
}

test_pinned_dep_passes if {
	count(package_json.deny) == 0 with input as {
		"name": "x",
		"engines": {"node": ">=22"},
		"type": "module",
		"dependencies": {"good-pkg": "^1.2.3"},
	}
}

test_wildcard_devdep_denied if {
	count(package_json.deny) > 0 with input as {
		"name": "x",
		"engines": {"node": ">=22"},
		"type": "module",
		"devDependencies": {"bad-dev": "*"},
	}
}
