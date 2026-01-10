# Dead Link Checker - Installation & Distribution Guide

## 📦 For End Users (Installing the Software)

### Option 1: Using the Installer (Recommended)

1. Download `DeadLinkChecker_Setup_v2.0.exe`
2. Double-click the installer
3. Follow the installation wizard:
   - Accept the license agreement
   - Choose installation directory (default: `C:\Program Files\DeadLinkChecker`)
   - Select if you want a desktop shortcut
   - Click Install
4. Launch Dead Link Checker from:
   - Start Menu → Dead Link Checker
   - Desktop shortcut (if created)

### Option 2: Standalone Executable

1. Download `DeadLinkChecker.exe`
2. Place it in any folder
3. Double-click to run
4. No installation needed!

## 🛠️ For Developers (Building the Installer)

### Prerequisites

Before building, ensure you have:

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/

2. **Inno Setup 6** (for creating the installer)
   - Download from: https://jrsoftware.org/isdl.php
   - Install with default settings

3. **Git** (optional, for cloning the repository)
   - Download from: https://git-scm.com/downloads

### Installation Steps

#### Step 1: Get the Source Code

```bash
git clone https://github.com/arif98741/deadlink-checker-python.git
cd deadlink-checker-python
```

Or download and extract the ZIP file from GitHub.

#### Step 2: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- requests (HTTP requests)
- beautifulsoup4 (HTML parsing)
- customtkinter (Modern GUI)
- pillow (Image support)
- reportlab (PDF generation)
- pyinstaller (Executable builder)

#### Step 3: Build the Installer

**Easy Way (Recommended):**

Simply double-click: `build_installer.bat`

**Or run from PowerShell:**

```powershell
.\build_installer.ps1
```

**Or run from Command Prompt:**

```cmd
powershell -ExecutionPolicy Bypass -File build_installer.ps1
```

### What Happens During Build

The build script will:

1. ✅ Check Python dependencies
2. ✅ Clean previous builds
3. ✅ Build executable with PyInstaller (~2-5 minutes)
4. ✅ Create Windows installer with Inno Setup (~30 seconds)
5. ✅ Show file sizes and locations

### Build Output

After successful build, you'll find:

```
📁 dist/
   └── DeadLinkChecker.exe          (Standalone executable, ~50-80 MB)

📁 installer_output/
   └── DeadLinkChecker_Setup_v2.0.exe   (Full installer, ~50-85 MB)
```

## 📤 Distribution

You can distribute either:

### 1. The Installer (Recommended for most users)
- **File**: `installer_output/DeadLinkChecker_Setup_v2.0.exe`
- **Pros**: 
  - Professional installation experience
  - Creates Start Menu shortcuts
  - Includes uninstaller
  - Organized file structure
- **Cons**: 
  - Users must run installer
  - Requires installation permissions

### 2. Standalone Executable (For portable use)
- **File**: `dist/DeadLinkChecker.exe`
- **Pros**: 
  - No installation needed
  - Can run from USB drive
  - Portable
- **Cons**: 
  - No shortcuts created
  - No uninstaller
  - Reports saved in same directory

## 🎨 Customization

### Change Version Number

Edit `installer_script.iss`:
```ini
AppVersion=2.1  ; Change this
OutputBaseFilename=DeadLinkChecker_Setup_v2.1  ; And this
```

### Add Custom Icon

1. Create or obtain an `.ico` file
2. Save as `icon.ico` in the project root
3. Edit `deadlink_gui.spec`:
   ```python
   icon='icon.ico',  # Uncomment and set this
   ```
4. Edit `installer_script.iss`:
   ```ini
   SetupIconFile=icon.ico  ; Already configured
   ```

### Add Installer Banner Images

Create two images:
- `installer_banner.bmp` (164 x 314 pixels) - Left side of installer
- `installer_small.bmp` (55 x 58 pixels) - Top right corner

Place in project root. Already configured in `installer_script.iss`.

### Change Publisher Information

Edit `installer_script.iss`:
```ini
AppPublisher=YourName
AppPublisherURL=https://yourwebsite.com
```

## 🔧 Troubleshooting

### "PyInstaller is not recognized"
```powershell
pip install pyinstaller
```

### "ISCC.exe not found"
- Install Inno Setup from: https://jrsoftware.org/isdl.php
- Use default installation path

### Build fails with "Module not found"
Add to `deadlink_gui.spec` under `hiddenimports`:
```python
hiddenimports=[
    'customtkinter',
    'your_missing_module',  # Add here
],
```

### Executable is too large
This is normal. The executable includes:
- Python runtime (~40 MB)
- All libraries and dependencies
- GUI framework
- PDF generation libraries

### Antivirus flags the executable
This is a false positive common with PyInstaller executables:
- Submit to antivirus vendor as false positive
- Code sign the executable (requires certificate)
- Users can add exception in their antivirus

## 📊 File Size Breakdown

Typical sizes:
- **Executable**: 50-80 MB
  - Python runtime: ~40 MB
  - Libraries: ~10-30 MB
  - Your code: <1 MB

- **Installer**: 50-85 MB (compressed)

## 🚀 Advanced: Code Signing (Optional)

For professional distribution, consider code signing:

1. Obtain a code signing certificate
2. Install certificate on your system
3. Edit `deadlink_gui.spec`:
   ```python
   codesign_identity='Your Certificate Name',
   ```

Benefits:
- Removes "Unknown Publisher" warning
- Reduces antivirus false positives
- Builds user trust

## 📝 Checklist Before Distribution

- [ ] Test the executable on a clean Windows machine
- [ ] Test the installer installation process
- [ ] Test the uninstaller
- [ ] Verify all features work in installed version
- [ ] Check reports are saved correctly
- [ ] Update version numbers
- [ ] Update README and documentation
- [ ] Create release notes
- [ ] Test on different Windows versions (10, 11)

## 🆘 Support

- **Issues**: https://github.com/arif98741/deadlink-checker-python/issues
- **Documentation**: See README.md and QUICKSTART.md
- **Email**: [Your contact email]

## 📜 License

This software is distributed under the MIT License.
See LICENSE.txt for details.

---

**Built with ❤️ by arif98741**

Version 2.0 | © 2026 All Rights Reserved
