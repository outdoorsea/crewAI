#!/bin/bash
# Simple script to run myndy_ai_beta.py without reinstalling

# Activate virtual environment
source venv/bin/activate

# Check if packages are installed, install if not
if ! python -c "import pydantic" 2>/dev/null; then
    echo "Installing dependencies (one-time setup)..."
    pip install pydantic fastapi uvicorn
fi

# Run the script
echo "Running myndy_ai_beta.py..."
python myndy_ai_beta.py "$@"