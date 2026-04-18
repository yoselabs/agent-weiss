#!/bin/sh
# universal.security.gitleaks-precommit
if [ ! -f .pre-commit-config.yaml ]; then
  printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": ".pre-commit-config.yaml missing"}'
  exit 1
fi
if grep -q 'gitleaks' .pre-commit-config.yaml; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "gitleaks hook configured in .pre-commit-config.yaml"}'
  exit 0
else
  printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": ".pre-commit-config.yaml present but no gitleaks hook entry"}'
  exit 1
fi
