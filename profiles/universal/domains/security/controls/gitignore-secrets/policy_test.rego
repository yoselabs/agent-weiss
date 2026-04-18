package universal.security.gitignore_secrets_test

import rego.v1
import data.universal.security.gitignore_secrets

test_missing_env_fires if {
	gitignore_secrets.deny with input as [
		{"Kind": "Path", "Value": "*.log", "Original": "*.log"},
	]
}

test_env_present_no_deny_for_dotenv if {
	count([msg | some msg in gitignore_secrets.deny; contains(msg, "'.env'")]) == 0 with input as [
		{"Kind": "Path", "Value": ".env", "Original": ".env"},
		{"Kind": "Path", "Value": ".env.*", "Original": ".env.*"},
	]
}

test_env_glob_present_no_deny_for_glob if {
	count([msg | some msg in gitignore_secrets.deny; contains(msg, "'.env.*'")]) == 0 with input as [
		{"Kind": "Path", "Value": ".env", "Original": ".env"},
		{"Kind": "Path", "Value": ".env.*", "Original": ".env.*"},
	]
}

test_only_env_no_glob_fires_glob_rule if {
	gitignore_secrets.deny with input as [
		{"Kind": "Path", "Value": ".env", "Original": ".env"},
	]
}
