#!/bin/bash
set -e

echo "Running ETL loop inside container..."
uv run python scripts/run_etl_loop.py

echo "Checking health endpoint..."
curl -f http://localhost:8000/health

echo "Checking data endpoint..."
curl -f "http://localhost:8000/data?limit=5"

echo "Smoke test PASSED"
