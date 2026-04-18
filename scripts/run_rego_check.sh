#!/bin/sh
# Shared Rego check.sh wrapper.
#
# Usage (from a control's check.sh):
#   sh "$AGENT_WEISS_BUNDLE/scripts/run_rego_check.sh" \
#     <target_relative_to_cwd> <policy_subpath_relative_to_bundle> [<data_json>]
#
# Reads $AGENT_WEISS_BUNDLE; emits one JSON line per the agent-weiss contract;
# exits 0 / 1 / 127 matching the JSON status.

set -e

if [ -z "$AGENT_WEISS_BUNDLE" ]; then
  printf '%s\n' '{"status": "setup-unmet", "summary": "AGENT_WEISS_BUNDLE not set", "install": "Install agent-weiss via Claude marketplace, PyPI, or npm — or set AGENT_WEISS_BUNDLE manually."}'
  exit 127
fi

TARGET="$1"
POLICY_SUBPATH="$2"
DATA_JSON="${3:-}"

if [ -z "$TARGET" ] || [ -z "$POLICY_SUBPATH" ]; then
  printf '%s\n' '{"status": "setup-unmet", "summary": "run_rego_check.sh requires <target> <policy_subpath> args"}'
  exit 127
fi

# Use the Python helper for parsing; relies on `python` being available.
PYTHON="${AGENT_WEISS_PYTHON:-python}"

EXIT_CODE=0
JSON_OUTPUT=$("$PYTHON" -c "
import json, sys
from pathlib import Path
from agent_weiss.lib.rego import run_rego_check

data = None
if '''$DATA_JSON''':
    data = json.loads('''$DATA_JSON''')

result = run_rego_check(
    target=Path('$TARGET'),
    policy=Path('$AGENT_WEISS_BUNDLE') / '$POLICY_SUBPATH',
    data=data,
)
print(json.dumps(result))
" ) || EXIT_CODE=$?

if [ "$EXIT_CODE" -ne 0 ] && [ -z "$JSON_OUTPUT" ]; then
  printf '%s\n' '{"status": "setup-unmet", "summary": "Python helper agent_weiss.lib.rego failed to run"}'
  exit 127
fi

STATUS=$(printf '%s' "$JSON_OUTPUT" | "$PYTHON" -c "import json, sys; print(json.loads(sys.stdin.read())['status'])")

printf '%s\n' "$JSON_OUTPUT"

case "$STATUS" in
  pass) exit 0 ;;
  fail) exit 1 ;;
  setup-unmet) exit 127 ;;
  *) exit 1 ;;
esac
