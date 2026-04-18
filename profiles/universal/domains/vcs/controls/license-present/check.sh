#!/bin/sh
for candidate in LICENSE LICENSE.md LICENSE.txt LICENSE.rst COPYING; do
  if [ -f "$candidate" ]; then
    printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "LICENSE present at project root"}'
    exit 0
  fi
done
printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": "no LICENSE file at project root"}'
exit 1
