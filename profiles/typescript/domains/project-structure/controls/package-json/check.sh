#!/bin/sh
exec sh "$AGENT_WEISS_BUNDLE/scripts/run_rego_check.sh" \
  "package.json" \
  "profiles/typescript/domains/project-structure/controls/package-json/policy.rego"
