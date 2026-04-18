#!/bin/sh
# universal.docs.agents-md-present
# Exit 0 + status:pass if AGENTS.md exists at the repo root.
# Exit 1 + status:fail otherwise.

if [ -f AGENTS.md ]; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "AGENTS.md present"}'
  exit 0
else
  printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": "AGENTS.md missing at project root"}'
  exit 1
fi
