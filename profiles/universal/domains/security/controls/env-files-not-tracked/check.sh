#!/bin/sh
# universal.security.env-files-not-tracked
# Walk the project tree for .env or .env.* files (excluding .env.example).
COUNT=$(find . -type f \( -name '.env' -o -name '.env.*' \) ! -name '.env.example' 2>/dev/null | wc -l | tr -d ' ')
if [ "$COUNT" = "0" ]; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "no .env files in tree"}'
  exit 0
else
  printf '%s\n' "{\"status\": \"fail\", \"findings_count\": $COUNT, \"summary\": \"$COUNT .env file(s) present in working tree — verify untracked or rename to .env.example\"}"
  exit 1
fi
