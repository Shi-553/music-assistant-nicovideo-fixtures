#!/usr/bin/env bash
set -euo pipefail

# Run fixture generator as a Python module
# This script activates the virtual environment and runs the fixture generator

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Activate virtual environment if it exists
if [ -f "${REPO_ROOT}/.venv/bin/activate" ]; then
    # shellcheck source=/dev/null
    source "${REPO_ROOT}/.venv/bin/activate"
fi

# Run the fixture generator as a Python module
cd "${REPO_ROOT}"
python -m fixture_generator.main "$@"
