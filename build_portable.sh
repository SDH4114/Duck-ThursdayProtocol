#!/bin/bash
set -e # Stop script on any error

# Define virtual environment directory
VENV_DIR="venv"

echo "Checking environment..."

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Install dependencies inside virtual environment
echo "Installing dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi
# Ensure PyInstaller is installed in the venv
pip install pyinstaller

# 4. Build
echo "Building Duck..."
# Use the python and pyinstaller from the venv
pyinstaller --clean --noconfirm --onefile --name Duck duck_portable.py

echo ""
echo "Build complete."
echo "Executable is at: dist/Duck"
echo ""
echo "You can move 'dist/Duck' anywhere or send it to a friend."
