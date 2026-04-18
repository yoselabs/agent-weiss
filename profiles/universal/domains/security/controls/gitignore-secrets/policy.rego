package universal.security.gitignore_secrets

# WHAT: .gitignore must exclude .env and .env.* files.
# WHY: Agents create .env with real secrets; without gitignore entries the
# next `git add .` leaks them.
# WITHOUT IT: Secrets in git history.
# FIX: Add `.env` and `.env.*` lines to .gitignore.
#
# Input: array of [{Kind, Value, Original}] entries from conftest's
# .gitignore parser.

import rego.v1

deny contains msg if {
	not _pattern_present(".env")
	msg := ".gitignore: '.env' is not excluded — agents create .env files containing real secrets"
}

deny contains msg if {
	not _pattern_present(".env.*")
	not _pattern_present(".env*")
	msg := ".gitignore: '.env.*' (or '.env*') is not excluded — variants like .env.local also leak secrets"
}

_pattern_present(pattern) if {
	some entry in input
	entry.Kind == "Path"
	entry.Value == pattern
}

_pattern_present(pattern) if {
	some entry in input
	entry.Kind == "Path"
	entry.Original == pattern
}
