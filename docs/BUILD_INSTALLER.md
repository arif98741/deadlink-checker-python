# Building the Windows Installer

This guide explains how to build a Windows installer for Dead Link Checker.

## Prerequisites

1. **Python 3.8+** with all dependencies installed
2. **Inno Setup 6** (or 5) - Download from: https://jrsoftware.org/isdl.php

## Quick Build

Simply run the build script:

```powershell
.\build_installer.ps1
```

This will:
1. Check and install Python dependencies
2. Build the executable using PyInstaller
3. Create a Windows installer using Inno Setup
4. Output the installer to `installer_output\DeadLinkChecker_Setup_v2.0.exe`

## Manual Build Process

If you prefer to build manually:

### Step 1: Build the Executable

```powershell
pyinstaller --clean deadlink_gui.spec
```

This creates `dist\DeadLinkChecker.exe`

### Step 2: Build the Installer

1. Install Inno Setup from https://jrsoftware.org/isdl.php
2. Open `installer_script.iss` in Inno Setup
3. Click "Build" → "Compile"
4. The installer will be created in `installer_output\`

## Installer Features

The installer includes:

✅ **Professional Installation Wizard**
- Modern UI with custom branding
- License agreement display
- Custom installation directory selection
- Desktop shortcut option (optional)
- Start menu shortcuts

✅ **Complete Package**
- Main application executable
- Documentation (README, Quick Start Guide)
- Reports directory
- Uninstaller

✅ **User-Friendly**
- No admin rights required (installs to user directory)
- Option to launch app after installation
- Clean uninstallation

## Distribution

After building, you can distribute:

- **installer_output\DeadLinkChecker_Setup_v2.0.exe** - Full installer (recommended)
- **dist\DeadLinkChecker.exe** - Standalone executable (no installation needed)

## File Sizes

- Executable: ~50-80 MB (includes Python runtime and all dependencies)
- Installer: ~50-85 MB (compressed)

## Customization

To customize the installer:

1. Edit `installer_script.iss`
2. Change version numbers, publisher info, URLs, etc.
3. Add custom icons by placing `icon.ico` in the root directory
4. Add installer banner images:
   - `installer_banner.bmp` (164x314 pixels)
   - `installer_small.bmp` (55x58 pixels)

## Troubleshooting

### "PyInstaller not found"
```powershell
pip install -r requirements.txt
```

### "Inno Setup not found"
Download and install from: https://jrsoftware.org/isdl.php

### Build fails with missing modules
Add the module to `hiddenimports` in `deadlink_gui.spec`

## Support

For issues, visit: https://github.com/arif98741/deadlink-checker-python/issues
