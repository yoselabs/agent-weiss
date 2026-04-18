#!/bin/sh
# typescript.testing.vitest-config
for candidate in vitest.config.ts vitest.config.js vitest.config.mjs; do
  if [ -f "$candidate" ]; then
    printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "vitest config file present"}'
    exit 0
  fi
done
if [ -f package.json ] && grep -q '"vitest"' package.json; then
  printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "vitest config in package.json"}'
  exit 0
fi
printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": "no vitest config (file or package.json block)"}'
exit 1
