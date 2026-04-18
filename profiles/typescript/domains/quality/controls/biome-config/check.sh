#!/bin/sh
# typescript.quality.biome-config
for candidate in biome.json biome.jsonc; do
  if [ -f "$candidate" ]; then
    if grep -q '{' "$candidate"; then
      printf '%s\n' '{"status": "pass", "findings_count": 0, "summary": "biome config present"}'
      exit 0
    fi
  fi
done
printf '%s\n' '{"status": "fail", "findings_count": 1, "summary": "no biome.json or biome.jsonc at project root"}'
exit 1
