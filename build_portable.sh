#!/bin/bash
# Build standalone Duck executable

# Ensure PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

echo "Building Duck..."
pyinstaller --clean --noconfirm --onefile --name Duck duck_portable.py

echo ""
echo "Build complete."
echo "Executable is at: dist/Duck"
echo ""
echo "You can move 'dist/Duck' anywhere or send it to a friend."
