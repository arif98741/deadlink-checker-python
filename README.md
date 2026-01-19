# 🔗 Dead Link Checker

**Version 2.1.2** | Professional Website Link Analysis & Reporting Tool

A powerful desktop application for analyzing and reporting broken links on websites. Built with Python and CustomTkinter, packaged as a standalone Windows executable.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)

---

## 📋 Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
  - [For End Users](#for-end-users)
  - [For Developers](#for-developers)
- [Usage](#usage)
- [Building from Source](#building-from-source)
  - [Prerequisites](#prerequisites)
  - [Build Steps](#build-steps)
  - [Manual Build](#manual-build)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Reports](#reports)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## ✨ Features

### Core Features
- ✅ **Comprehensive Link Checking** - Analyze unlimited links on any website
- ✅ **Recursive Crawling** - Follow internal links with configurable depth (1-5 levels)
- ✅ **Real-time Progress** - Live updates as links are being checked
- ✅ **Concurrent Processing** - Adjustable workers (5-50) for faster analysis
- ✅ **Detailed Statistics** - Total links, working, broken, and success rate

### Report Generation
- ✅ **Multiple Formats** - Export reports in TXT, PDF, and CSV formats
- ✅ **Professional PDF Reports** - Tabular format with color-coded status
- ✅ **CSV Export** - Easy data analysis in Excel or other tools
- ✅ **Automatic Naming** - Reports saved with timestamp for easy tracking

### User Interface
- ✅ **Modern GUI** - Clean, professional interface with dark mode
- ✅ **Easy Configuration** - Intuitive sliders and checkboxes
- ✅ **Progress Monitoring** - Real-time status updates and progress bar
- ✅ **Statistics Dashboard** - Live stats cards showing analysis results

### Technical Features
- ✅ **Standalone Executable** - No Python installation required
- ✅ **Professional Installer** - Full installation wizard with shortcuts
- ✅ **Version Information** - Embedded metadata in executable
- ✅ **Error Handling** - Robust error handling and logging

---

## 📸 Screenshots

*(Add screenshots of your application here)*

---

## 💾 Installation

### For End Users

#### Option 1: Using the Installer (Recommended)

1. **Download** the installer:
   ```
   DeadLinkChecker_Setup_v2.0.exe
   ```

2. **Run** the installer by double-clicking it

3. **Follow** the installation wizard:
   - Welcome screen
   - Read quick start information
   - Accept the license agreement
   - Choose installation directory (default: `C:\Program Files\DeadLinkChecker`)
   - Select Start Menu folder
   - Choose additional shortcuts (Desktop, Quick Launch)
   - Review installation summary
   - Install
   - Launch the application

4. **Launch** from:
   - Start Menu → Dead Link Checker
   - Desktop shortcut (if created)
   - Installation directory

#### Option 2: Portable Executable

1. **Download** the standalone executable:
   ```
   DeadLinkChecker_v2.0.exe
   ```

2. **Place** it in any folder

3. **Double-click** to run (no installation needed)

### For Linux Users

1. **Ensure Python 3.8+** and `tkinter` are installed:
   ```bash
   sudo apt-get install python3-tk  # Ubuntu/Debian
   sudo apt-get install libappindicator3-1 # For System Tray
   ```
2. **Install requirements**:
   ```bash
   pip3 install -r build_tools/requirements.txt
   ```
3. **Run the script**:
   ```bash
   ./run.sh
   ```

### Building Standalone Linux App (Installer)

If you want to create a standalone binary and install it to your system (menu shortcut, icons):

1. **Build the bundle**:
   ```bash
   chmod +x build_tools/build_linux.sh
   ./build_tools/build_linux.sh
   ```
   This will create a `DeadLinkChecker_v2.1.2_linux_x64.tar.gz` and a `deadlinkchecker_2.1.2_amd64.deb` in the `installer_output/` folder.
2. **Install the app**:
   - **Method A: Using .deb (Recommended for Ubuntu/Debian)**:
     ```bash
     sudo dpkg -i installer_output/deadlinkchecker_2.1.2_amd64.deb
     ```
   - **Method B: Using .tar.gz bundle**:
     ```bash
     # Extract the bundle
     cd installer_output
     tar -xzf DeadLinkChecker_v2.1.2_linux_x64.tar.gz -C .
     # Run the installer script
     ./install.sh
     ```
   This will add the app to your application menu and create a terminal command `deadlinkchecker`.

### For Developers

See [Building from Source](#building-from-source) section below.

---

## 🚀 Usage

### Quick Start

1. **Launch** the application

2. **Enter** the website URL you want to analyze:
   ```
   https://example.com
   ```

3. **Configure** analysis settings:
   - **Crawl Depth**: 1 = Homepage only, 2+ = Follow internal links
   - **Concurrent Workers**: 5-50 (higher = faster but more resource intensive)
   - **Timeout**: 5-30 seconds per link

4. **Select** report formats:
   - ☑ Generate Text Report (.txt)
   - ☑ Generate PDF Report (.pdf)
   - ☑ Generate CSV Report (.csv)

5. **Click** "Start Analysis"

6. **Monitor** progress in real-time:
   - Status updates in the text area
   - Progress bar showing completion
   - Live statistics (Total, Working, Broken, Success Rate)

7. **View** results:
   - Reports automatically saved in `reports/` folder
   - Click "Open Reports Folder" to access them

### Advanced Usage

#### Crawl Depth Explained

- **Depth 1**: Checks only links found on the homepage
- **Depth 2**: Checks homepage + all internal pages linked from homepage
- **Depth 3**: Goes 3 levels deep into the website
- **Depth 4-5**: For comprehensive site-wide analysis

#### Workers Configuration

- **5-10 workers**: Conservative, good for slower connections
- **10-20 workers**: Balanced, recommended for most users
- **20-50 workers**: Aggressive, for fast connections and large sites

#### Timeout Settings

- **5-10 seconds**: For fast, reliable websites
- **10-20 seconds**: Standard timeout for most sites
- **20-30 seconds**: For slow or unreliable websites

---

## 🛠️ Building from Source

### Prerequisites

#### Required Software

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Inno Setup 6** (for creating the installer)
   - Download from: https://jrsoftware.org/isdl.php
   - Install to default location or note custom path

3. **Git** (optional, for cloning repository)
   - Download from: https://git-scm.com/downloads

#### Python Dependencies

All dependencies are listed in `build_tools/requirements.txt`:
- `requests>=2.28.0` - HTTP requests
- `beautifulsoup4>=4.11.0` - HTML parsing
- `customtkinter>=5.2.0` - Modern GUI framework
- `pillow>=10.0.0` - Image support
- `reportlab>=4.0.0` - PDF generation
- `pyinstaller>=6.0.0` - Executable builder

### Build Steps

#### Step 1: Get the Source Code

**Option A: Clone from GitHub**
```bash
git clone https://github.com/arif98741/deadlink-checker-python.git
cd deadlink-checker-python
```

**Option B: Download ZIP**
- Download from GitHub
- Extract to a folder
- Open terminal in that folder

#### Step 2: Install Python Dependencies

```powershell
cd build_tools
pip install -r requirements.txt
```

This installs all required packages including PyInstaller.

#### Step 3: Build the Application

**Easy Way (Recommended):**

From project root:
```powershell
.\BUILD.ps1
```

Or from `build_tools` directory:
```powershell
cd build_tools
.\build_installer.ps1
```

**What happens:**
1. ✅ Checks Python dependencies
2. ✅ Cleans previous builds
3. ✅ Builds executable with PyInstaller (~3-5 minutes)
4. ✅ Searches for Inno Setup
5. ✅ Creates Windows installer (~30 seconds)

**Output:**
```
build_tools\dist\DeadLinkChecker_v2.0.exe          (Standalone executable)
installer_output\DeadLinkChecker_Setup_v2.0.exe    (Windows installer)
```

### Manual Build

If you need more control or have Inno Setup in a custom location:

#### Build Executable Only

```powershell
cd build_tools
pyinstaller --clean deadlink_gui.spec
```

Output: `build_tools\dist\DeadLinkChecker_v2.0.exe`

#### Build Installer Manually

**If Inno Setup is in default location:**
```powershell
cd build_tools
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

**If Inno Setup is in custom location (e.g., D: drive):**
```powershell
cd build_tools
&"D:\Inno Setup 6\ISCC.exe" installer_script.iss
```

```
cd build_tools; pwsh -ExecutionPolicy Bypass -File .\version_manager.ps1 && pyinstaller --clean deadlink_gui.spec && & "D:\Inno Setup 6\ISCC.exe" installer_script.iss && cd ..
```

**Or use the manual build script:**
```powershell
cd build_tools
.\build_installer_manual.ps1
```
This will prompt you for the ISCC.exe location.

Output: `..\installer_output\DeadLinkChecker_Setup_v2.0.exe`

### Build Configuration

#### Customizing the Build

**Change Version Number:**

Edit `build_tools/deadlink_gui.spec`:
```python
name='DeadLinkChecker_v3.0',  # Change version here
```

Edit `build_tools/version_info.txt`:
```python
filevers=(3, 0, 0, 0),  # Update version
prodvers=(3, 0, 0, 0),
```

Edit `build_tools/installer_script.iss`:
```ini
AppVersion=3.0
OutputBaseFilename=DeadLinkChecker_Setup_v3.0
```

**Add Custom Icon:**

1. Create or obtain an `.ico` file (256x256 recommended)
2. Save as `build_tools/icon.ico`
3. Uncomment in `build_tools/installer_script.iss`:
   ```ini
   SetupIconFile=icon.ico
   ```
4. Uncomment in `build_tools/deadlink_gui.spec`:
   ```python
   icon='icon.ico',
   ```

**Add Installer Banner Images:**

1. Create images:
   - `installer_banner.bmp` (164 x 314 pixels)
   - `installer_small.bmp` (55 x 58 pixels)
2. Place in `build_tools/` folder
3. Uncomment in `installer_script.iss`:
   ```ini
   WizardImageFile=installer_banner.bmp
   WizardSmallImageFile=installer_small.bmp
   ```

---

## 📁 Project Structure

```
deadlink-checker-python/
│
├── src/                          # Source Code
│   ├── deadlink_checker.py       # Core link checking logic
│   └── deadlink_gui.py           # GUI application
│
├── docs/                         # Documentation
│   ├── README.md                 # This file
│   ├── QUICKSTART.md             # Quick start guide
│   ├── LICENSE.txt               # MIT License
│   ├── BUILD_INSTALLER.md        # Build instructions
│   ├── BUILD_REFERENCE.txt       # Quick reference
│   ├── BUILD_FIXES.md            # Build fixes applied
│   ├── INSTALLATION_GUIDE.md     # Installation guide
│   ├── INSTALLER_SETUP_SUMMARY.md # Installer setup
│   ├── VERSIONED_FILENAME.md     # Versioning info
│   └── INSTALLER_WIZARD_GUIDE.md # Wizard documentation
│
├── build_tools/                  # Build Configuration
│   ├── build_installer.ps1       # Main build script
│   ├── build_installer.bat       # Batch wrapper
│   ├── build_installer_manual.ps1 # Manual build script
│   ├── build.ps1                 # Simple build script
│   ├── deadlink_gui.spec         # PyInstaller config
│   ├── installer_script.iss      # Inno Setup config
│   ├── version_info.txt          # Version metadata
│   ├── installation_complete.txt # Post-install info
│   └── requirements.txt          # Python dependencies
│
├── assets/                       # Assets & Resources
│   ├── sc.png                    # Screenshot
│   └── run_gui.bat               # Quick launcher
│
├── reports/                      # Generated Reports
│   └── .gitkeep                  # Keep directory in git
│
├── dist/                         # Built Executables (generated)
│   └── DeadLinkChecker_v2.0.exe
│
├── build/                        # Build artifacts (generated)
│
├── installer_output/             # Installers (generated)
│   └── DeadLinkChecker_Setup_v2.0.exe
│
├── .git/                         # Git repository
├── .gitignore                    # Git ignore rules
├── BUILD.ps1                     # Root build launcher
├── BUILD.bat                     # Root build launcher (batch)
├── restructure.ps1               # Project restructure script
├── restructure.bat               # Restructure launcher
├── RESTRUCTURE_GUIDE.md          # Restructure documentation
└── PROJECT_STRUCTURE.md          # Project structure guide
```

### Key Directories

- **`src/`** - All Python source code
- **`docs/`** - All documentation files
- **`build_tools/`** - Build scripts and configuration
- **`assets/`** - Images, icons, and resources
- **`reports/`** - Output directory for generated reports
- **`dist/`** - Built executables (created by PyInstaller)
- **`installer_output/`** - Windows installers (created by Inno Setup)

---

## ⚙️ Configuration

### Application Settings

Settings are configured through the GUI:

- **URL**: Website to analyze
- **Crawl Depth**: 1-5 levels
- **Workers**: 5-50 concurrent threads
- **Timeout**: 5-30 seconds
- **Report Formats**: TXT, PDF, CSV

### Build Configuration

Configuration files in `build_tools/`:

- **`deadlink_gui.spec`** - PyInstaller configuration
  - Hidden imports
  - Executable name
  - Version info
  - Icon settings

- **`installer_script.iss`** - Inno Setup configuration
  - App information
  - Installation directories
  - Shortcuts
  - Wizard pages
  - Custom messages

- **`version_info.txt`** - Windows version metadata
  - File version
  - Product version
  - Company name
  - Copyright

---

## 📊 Reports

### Report Formats

#### Text Report (.txt)
- Plain text format
- Summary statistics
- Detailed link list with status codes
- Easy to read and share

#### PDF Report (.pdf)
- Professional tabular format
- Color-coded status (green/red)
- Summary section
- Detailed results table
- Suitable for presentations

#### CSV Report (.csv)
- Spreadsheet-compatible format
- Columns: URL, Status Code, Status Text, Response Time, Link Type, Found On, Is Dead, Is External
- Easy data analysis in Excel
- Suitable for further processing

### Report Location

Reports are saved in:
- **Installed version**: `C:\Program Files\DeadLinkChecker\reports\`
- **Portable version**: `reports\` folder next to executable
- **Development**: `reports\` folder in project root

### Report Naming

Reports are automatically named with timestamps:
```
deadlink_report_example_com_20260110_215637.txt
deadlink_report_example_com_20260110_215637.pdf
deadlink_report_example_com_20260110_215637.csv
```

Format: `deadlink_report_[domain]_[YYYYMMDD]_[HHMMSS].[ext]`

---

## 🐛 Troubleshooting

### Common Issues

#### Build Issues

**"PyInstaller not found"**
```powershell
pip install pyinstaller
```

**"Inno Setup not found"**
- Install from: https://jrsoftware.org/isdl.php
- Or specify custom path in build script

**"Module not found" during build**
- Add to `deadlink_gui.spec` under `hiddenimports`:
  ```python
  hiddenimports=[
      'your_missing_module',
  ],
  ```

**Build fails with path errors**
- Make sure you're in the `build_tools` directory
- Or use the root `BUILD.ps1` script

#### Runtime Issues

**Antivirus flags the executable**
- This is a false positive (common with PyInstaller)
- Add exception in antivirus software
- Or submit to antivirus vendor as false positive

**"Windows protected your PC" message**
- Click "More info"
- Click "Run anyway"
- This happens because the executable is not code-signed

**Application doesn't start**
- Check if antivirus blocked it
- Try running from command line to see errors
- Check Windows Event Viewer for error details

**Reports not saving**
- Check folder permissions
- Make sure `reports/` folder exists
- Check disk space

#### Installation Issues

**Installer won't run**
- Right-click → "Run as administrator"
- Check antivirus settings
- Download installer again (may be corrupted)

**Installation fails**
- Check disk space (need ~100 MB)
- Close other applications
- Try different installation directory

### Getting Help

If you encounter issues:

1. **Check Documentation**
   - Read relevant `.md` files in `docs/` folder
   - Check `BUILD_FIXES.md` for known issues

2. **Check Logs**
   - PyInstaller logs in build output
   - Inno Setup logs in installer output
   - Application logs (if implemented)

3. **Report Issues**
   - GitHub Issues: https://github.com/arif98741/deadlink-checker-python/issues
   - Include:
     - Error message
     - Steps to reproduce
     - System information (Windows version, Python version)
     - Screenshots if applicable

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check if the bug is already reported in Issues
2. Create a new issue with:
   - Clear title
   - Detailed description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/logs if applicable

### Suggesting Features

1. Check if the feature is already requested
2. Create a new issue with:
   - Clear description of the feature
   - Use case / why it's needed
   - Proposed implementation (optional)

### Code Contributions

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test thoroughly
5. Commit with clear messages:
   ```bash
   git commit -m "Add: feature description"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

### Development Setup

1. Clone the repository
2. Install dependencies:
   ```powershell
   cd build_tools
   pip install -r requirements.txt
   ```
3. Make changes in `src/` directory
4. Test by running:
   ```powershell
   python src/deadlink_gui.py
   ```
5. Build to test executable:
   ```powershell
   cd build_tools
   .\build_installer.ps1
   ```

---

## 📜 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2026 arif98741

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See [LICENSE.txt](docs/LICENSE.txt) for full license text.

---

## 📞 Contact

- **Author**: arif98741
- **Website**: https://devtobox.com
- **GitHub**: https://github.com/arif98741/deadlink-checker-python
- **Issues**: https://github.com/arif98741/deadlink-checker-python/issues

---

## 🙏 Acknowledgments

- **CustomTkinter** - Modern GUI framework
- **PyInstaller** - Executable builder
- **Inno Setup** - Windows installer creator
- **ReportLab** - PDF generation
- **Beautiful Soup** - HTML parsing
- **Requests** - HTTP library

---

## 📈 Version History

### Version 2.1.2 (Current)
- ✅ Enhanced Windows responsiveness (Fixed "Not Responding" issues)
- ✅ Improved history loading with progressive rendering
- ✅ Redesigned action buttons (Start, Stop, Pause) for a premium look
- ✅ Added "Check External Links" toggle in sidebar
- ✅ Asynchronous system notifications and tray initialization
- ✅ Cross-platform support (Linux & macOS) with `run.sh`
- ✅ Modular project structure for better maintainability

### Version 2.1.1
- ✅ Basic link checking functionality
- ✅ TXT and PDF report generation
- ✅ Command-line interface
- ✅ Simple GUI

---

## 🎯 Roadmap

Future enhancements planned:

- [ ] Support for authentication (login-protected sites)
- [ ] Scheduled link checking
- [ ] Email notifications
- [ ] Link history tracking
- [ ] Comparison between scans
- [ ] Export to Excel format
- [ ] Custom report templates
- [ ] Multi-language support
- [ ] macOS and Linux support
- [ ] Cloud storage integration

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Built with ❤️ by arif98741**

**© 2026 All Rights Reserved**

**Version 2.1.2**
