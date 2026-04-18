#!/bin/sh
# universal.docs.claude-md-present
if [ -f CLAUDE.md ]; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "CLAUDE.md present"}'
  exit 0
else
  printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": "CLAUDE.md missing at project root"}'
  exit 1
fi
