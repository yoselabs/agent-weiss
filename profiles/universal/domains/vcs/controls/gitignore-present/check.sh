#!/bin/sh
if [ -f .gitignore ]; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": ".gitignore present"}'
  exit 0
else
  printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": ".gitignore missing at project root"}'
  exit 1
fi
