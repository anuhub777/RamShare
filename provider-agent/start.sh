#!/usr/bin/env bash
# Quick-start script for RAMShare Provider Agent
set -e

echo "=========================================="
echo "    RAMShare Provider Agent Launcher      "
echo "=========================================="

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required. Please install Python 3.10+."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Ensuring dependencies are installed..."
pip install -r requirements.txt --quiet

API_URL="${1:-http://localhost:8000}"
echo "Connecting to RAMShare backend at: $API_URL"
python3 -m agent.main start --api-url "$API_URL"
