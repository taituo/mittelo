#!/bin/bash
set -e

# 1. Ensure uv is available
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# 2. Ensure virtualenv exists and has textual
if [ ! -d ".venv" ]; then
    echo "Creating virtualenv..."
    uv venv
fi

echo "Installing/Updating dependencies..."
uv pip install textual

# 3. Launch Dashboard
echo "Launching Mittelö Mission Control..."
# Run python module from the venv
# Assuming we are in project root
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
uv run python3 -m mittelo dashboard --port 8765
