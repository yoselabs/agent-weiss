#!/bin/sh
# universal.security.gitignore-secrets
# Delegates to shared Rego runner. Target: .gitignore (parsed by conftest).
exec sh "$AGENT_WEISS_BUNDLE/scripts/run_rego_check.sh" \
  ".gitignore" \
  "profiles/universal/domains/security/controls/gitignore-secrets/policy.rego"
