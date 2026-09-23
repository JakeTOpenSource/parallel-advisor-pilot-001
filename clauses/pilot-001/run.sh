#!/bin/sh
# Pilot clause 001 public runner.
# Usage: bash run.sh [track]   (track defaults to M)
# Writes result.json next to this script. Exits nonzero on suite failure.
set -e
cd "$(dirname "$0")"
PAS_TRACK="${1:-M}" python3 suite.py > result.json
echo "wrote result.json"
