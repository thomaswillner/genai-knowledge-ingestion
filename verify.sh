#!/usr/bin/env bash
# One-command test harness (spec section 13: Verification Gates).
# Runs: schema validation, scope/labeling/quality conformance suites,
# sensitive-data gates, chunking determinism, end-to-end reference run.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! "$PYTHON" -c "import tiktoken, jsonschema, pytest" 2>/dev/null; then
  echo "Missing dependencies. Install with:"
  echo "  $PYTHON -m pip install -r reference/requirements.txt"
  exit 2
fi

exec "$PYTHON" -m pytest reference/tests -q "$@"
