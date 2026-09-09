#!/usr/bin/env bash
echo "Starting ConsciousCore V1 System Diagnostics..."
PYTHONPATH=backend python3 -m pytest backend/tests
