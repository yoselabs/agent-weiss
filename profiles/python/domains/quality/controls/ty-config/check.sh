#!/bin/sh
# python.quality.ty-config — verify [tool.ty] block exists in pyproject.toml.
if [ ! -f pyproject.toml ]; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "pyproject.toml not present — control not applicable"}'
  exit 0
fi
if grep -q '^\[tool\.ty\]' pyproject.toml; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "[tool.ty] section configured"}'
  exit 0
else
  printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": "pyproject.toml has no [tool.ty] section"}'
  exit 1
fi
