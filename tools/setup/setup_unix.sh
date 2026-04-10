#!/usr/bin/env bash
set -euo pipefail

echo
echo "Playwright Core Framework Setup"
echo "Running macOS/Linux setup..."

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "Python was not found in PATH. Please install Python 3.11+ and try again."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  "$PYTHON_CMD" -m venv .venv
else
  echo "Virtual environment already exists."
fi

VENV_PYTHON=".venv/bin/python"

echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

echo "Installing framework in editable mode..."
"$VENV_PYTHON" -m pip install -e .

echo "Installing Playwright browsers..."
"$VENV_PYTHON" -m playwright install

echo
echo "Setup completed successfully."
echo "Run tests with:"
echo ".venv/bin/python -m playwright_core.testing.testng_runner automation/testng.xml"

