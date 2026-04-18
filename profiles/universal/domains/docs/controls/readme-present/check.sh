#!/bin/sh
# universal.docs.readme-present — accept any conventional README spelling.
for candidate in README.md README.rst README.txt README; do
  if [ -f "$candidate" ]; then
    printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "README present at project root"}'
    exit 0
  fi
done
printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": "no README.* found at project root"}'
exit 1
