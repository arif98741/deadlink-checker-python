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
echo "Packaging for Linux (.tar.gz)..."
PACKAGE_NAME="DeadLinkChecker_v2.1.2_linux_x64.tar.gz"
TEMP_PKG="$DIST_DIR/pkg"
mkdir -p "$TEMP_PKG"
cp "$DIST_DIR/DeadLinkChecker" "$TEMP_PKG/"
cp "$BUILD_DIR/install_linux.sh" "$TEMP_PKG/install.sh"
chmod +x "$TEMP_PKG/install.sh"

cd "$DIST_DIR"
tar -czf "$INSTALLER_DIR/$PACKAGE_NAME" -C "$TEMP_PKG" .

# 6. Create Debian Package (.deb)
if command -v dpkg-deb &> /dev/null; then
    echo "Packaging for Linux (.deb)..."
    DEB_ROOT="$DIST_DIR/deb"
    DEB_NAME="deadlinkchecker_2.1.2_amd64"
    
    mkdir -p "$DEB_ROOT/usr/bin"
    mkdir -p "$DEB_ROOT/usr/share/applications"
    mkdir -p "$DEB_ROOT/DEBIAN"
    
    # Copy binary
    cp "$DIST_DIR/DeadLinkChecker" "$DEB_ROOT/usr/bin/deadlinkchecker"
    chmod +x "$DEB_ROOT/usr/bin/deadlinkchecker"
    
    # Create Desktop Entry
    cat <<EOF > "$DEB_ROOT/usr/share/applications/deadlinkchecker.desktop"
[Desktop Entry]
Version=2.1.2
Type=Application
Name=Dead Link Checker
Comment=Professional Website Link Analysis Tool
Exec=/usr/bin/deadlinkchecker
Icon=html
Terminal=false
Categories=Development;Network;
EOF

    # Create Control File
    cat <<EOF > "$DEB_ROOT/DEBIAN/control"
Package: deadlinkchecker
Version: 2.1.2
Section: utils
Priority: optional
Architecture: amd64
Maintainer: arif98741 <https://devtobox.com>
Description: Professional Website Link Analysis Tool
 Dead Link Checker is a professional tool for analyzing and reporting 
 broken links on websites. Distributed as a standalone binary.
EOF

    dpkg-deb --build "$DEB_ROOT" "$INSTALLER_DIR/${DEB_NAME}.deb"
fi

echo "========================================"
echo "BUILD COMPLETE!"
echo "Linux Tarball: $INSTALLER_DIR/$PACKAGE_NAME"
if [ -f "$INSTALLER_DIR/${DEB_NAME}.deb" ]; then
    echo "Linux Debian:  $INSTALLER_DIR/${DEB_NAME}.deb"
fi
echo "========================================"
