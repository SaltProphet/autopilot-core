#!/bin/bash
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH=src
python3 -m picore.ui.app &
python3 -m picore.pipeline.run
