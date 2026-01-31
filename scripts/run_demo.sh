#!/bin/bash
# Wrapper to run the demo script from the project root, regardless of current directory

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Always run the real demo script from pi-core/scripts
bash "$PROJECT_ROOT/pi-core/scripts/run_demo.sh" "$@"
