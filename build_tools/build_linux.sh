#!/bin/bash
# Dead Link Checker - Linux Build Script

# 1. Setup
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
BUILD_DIR="$PROJECT_ROOT/build_tools"
DIST_DIR="$PROJECT_ROOT/dist_linux"

cd "$PROJECT_ROOT"

# 2. Check for dependencies
echo "Checking dependencies..."
python3 -m pip install -r "$BUILD_DIR/requirements.txt"
python3 -m pip install pyinstaller

# 3. Clean previous builds
echo "Cleaning old builds..."
rm -rf "$DIST_DIR"
rm -rf "$PROJECT_ROOT/build"

# 4. Run PyInstaller
echo "Building Linux Binary..."
pyinstaller --noconfirm \
    --onefile \
    --windowed \
    --name "DeadLinkChecker_v2.1.2_linux" \
    --add-data "src/deadlink:deadlink" \
    --hidden-import "PIL._tkinter_finder" \
    --hidden-import "plyer.platforms.linux.notification" \
    --hidden-import "pystray._appindicator" \
    --collect-all "customtkinter" \
    --collect-all "CTkTable" \
    --distpath "$DIST_DIR" \
    "src/deadlink_gui.py"

echo "========================================"
echo "BUILD COMPLETE!"
echo "Binary located at: $DIST_DIR/DeadLinkChecker_v2.1.2_linux"
echo "========================================"
