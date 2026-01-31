#!/bin/bash
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH=src
PYTHON_BIN="python3.11"
if ! command -v $PYTHON_BIN &> /dev/null; then
	PYTHON_BIN="python3.12"
fi
$PYTHON_BIN -m picore.ui.app &
$PYTHON_BIN -m picore.pipeline.run
