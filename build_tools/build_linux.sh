#!/bin/bash
# Dead Link Checker - Linux Build Script

# 1. Setup
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
BUILD_DIR="$PROJECT_ROOT/build_tools"
DIST_DIR="$PROJECT_ROOT/dist_linux"
INSTALLER_DIR="$PROJECT_ROOT/installer_output"

cd "$PROJECT_ROOT"

# 2. Check for dependencies
echo "Checking dependencies..."
python3 -m pip install -r "$BUILD_DIR/requirements.txt"
python3 -m pip install pyinstaller

# 3. Clean previous builds
echo "Cleaning old builds..."
rm -rf "$DIST_DIR"
rm -rf "$PROJECT_ROOT/build"
mkdir -p "$INSTALLER_DIR"

# 4. Run PyInstaller
echo "Building Linux Binary..."
pyinstaller --noconfirm \
    --onefile \
    --windowed \
    --name "DeadLinkChecker" \
    --add-data "src/deadlink:deadlink" \
    --hidden-import "PIL._tkinter_finder" \
    --hidden-import "plyer.platforms.linux.notification" \
    --hidden-import "pystray._appindicator" \
    --collect-all "customtkinter" \
    --collect-all "CTkTable" \
    --distpath "$DIST_DIR" \
    "src/deadlink_gui.py"

# 5. Create Installer Bundle (.tar.gz)
echo "Packaging for Linux..."
PACKAGE_NAME="DeadLinkChecker_v2.1.2_linux_x64.tar.gz"
TEMP_PKG="$DIST_DIR/pkg"
mkdir -p "$TEMP_PKG"
cp "$DIST_DIR/DeadLinkChecker" "$TEMP_PKG/"
cp "$BUILD_DIR/install_linux.sh" "$TEMP_PKG/install.sh"
chmod +x "$TEMP_PKG/install.sh"

cd "$DIST_DIR"
tar -czf "$INSTALLER_DIR/$PACKAGE_NAME" -C "$TEMP_PKG" .

echo "========================================"
echo "BUILD COMPLETE!"
echo "Linux Package: $INSTALLER_DIR/$PACKAGE_NAME"
echo "========================================"
