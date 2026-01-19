#!/bin/bash
# Dead Link Checker - Linux Installer Script

APP_NAME="DeadLinkChecker"
APP_VERSION="2.1.2"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "========================================"
echo "Installing $APP_NAME v$APP_VERSION"
echo "========================================"

# 1. Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

# 2. Copy binary (assuming it's built or in current dir)
if [ -f "./DeadLinkChecker_v2.1.2_linux" ]; then
    cp "./DeadLinkChecker_v2.1.2_linux" "$INSTALL_DIR/deadlinkchecker"
    chmod +x "$INSTALL_DIR/deadlinkchecker"
else
    echo "Error: Binary not found in current directory."
    echo "Please run build_linux.sh first."
    exit 1
fi

# 3. Create symbolic link
ln -sf "$INSTALL_DIR/deadlinkchecker" "$BIN_DIR/deadlinkchecker"

# 4. Create Desktop Entry
cat <<EOF > "$DESKTOP_DIR/deadlinkchecker.desktop"
[Desktop Entry]
Version=$APP_VERSION
Type=Application
Name=Dead Link Checker
Comment=Professional Website Link Analysis Tool
Exec=$INSTALL_DIR/deadlinkchecker
Icon=html
Terminal=false
Categories=Development;Network;
EOF

chmod +x "$DESKTOP_DIR/deadlinkchecker.desktop"

echo "Success! $APP_NAME has been installed."
echo "You can now find it in your application menu or run 'deadlinkchecker' from terminal."
echo "========================================"
