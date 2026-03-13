#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
PYTHON_SCRIPT="$SCRIPT_DIR/chat.py"

# Function to setup venv
setup_venv() {
    echo "Initializing local virtual environment in .venv..."
    python3 -m venv "$VENV_DIR"
    
    echo "Installing dependencies..."
    "$VENV_DIR/bin/pip" install -q -r "$REQUIREMENTS_FILE"
    
    echo "Setup complete."
}

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    setup_venv
fi

# Run the script using the venv's python
# Pass all arguments ($@) to the python script
"$VENV_DIR/bin/python" "$PYTHON_SCRIPT" "$@"
