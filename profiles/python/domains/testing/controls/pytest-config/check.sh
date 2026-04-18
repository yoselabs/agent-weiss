#!/bin/sh
exec sh "$AGENT_WEISS_BUNDLE/scripts/run_rego_check.sh" \
  "pyproject.toml" \
  "profiles/python/domains/testing/controls/pytest-config/policy.rego"
