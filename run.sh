#!/bin/bash
# Dead Link Checker - Linux Launcher

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Determine script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Install requirements if needed
if [ "$1" == "--install" ]; then
    echo "Installing requirements..."
    pip3 install -r build_tools/requirements.txt
fi

# Run the app
python3 src/deadlink_gui.py
