#!/usr/bin/env bash
set -euo pipefail

HEADLESS_VALUE="${HEADLESS:-true}"
SLOW_MO_VALUE="${SLOW_MO:-0}"
TARGET=""

if [ "${1:-}" = "--headed" ]; then
  export HEADLESS=false
  if [ -n "${2:-}" ]; then
    export SLOW_MO="$2"
    shift 2
  else
    export SLOW_MO=400
    shift 1
  fi
fi

TARGET="${1:-}"

echo
echo "Playwright Core Test Runner"

if [ ! -f ".venv/bin/python" ]; then
  echo "Virtual environment not found. Run ./tools/setup/setup_unix.sh first."
  exit 1
fi

echo "HEADLESS=${HEADLESS:-$HEADLESS_VALUE}"
echo "SLOW_MO=${SLOW_MO:-$SLOW_MO_VALUE}"

if [ -n "$TARGET" ]; then
  echo "Running target: $TARGET"
  .venv/bin/python -B -m pytest "$TARGET"
else
  echo "Running automation/testng.xml ..."
  .venv/bin/python -B -m playwright_core.testing.testng_runner automation/testng.xml
fi
