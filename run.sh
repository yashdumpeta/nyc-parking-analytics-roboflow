#!/usr/bin/env bash
# Convenience runner script for NYC Parking Analytics Fullstack Platform

set -e

# Activate virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Execute unified Python runner
python3 run.py
