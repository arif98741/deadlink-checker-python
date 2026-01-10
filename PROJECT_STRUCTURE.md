# Dead Link Checker - Project Structure

## 📁 Directory Structure

```
deadlink-checker-python/
├── src/                          # Source Code
│   ├── deadlink_checker.py       # Core link checking logic
│   └── deadlink_gui.py           # GUI application
│
├── docs/                         # Documentation
│   ├── README.md                 # Project overview
│   ├── QUICKSTART.md             # Quick start guide
│   ├── LICENSE.txt               # MIT License
│   ├── BUILD_INSTALLER.md        # Build instructions
│   ├── BUILD_REFERENCE.txt       # Quick reference
│   ├── BUILD_FIXES.md            # Build fixes applied
│   ├── INSTALLATION_GUIDE.md     # Installation guide
│   ├── INSTALLER_SETUP_SUMMARY.md # Installer setup summary
│   └── VERSIONED_FILENAME.md     # Versioning info
│
├── build_tools/                  # Build Configuration
│   ├── build_installer.ps1       # Main build script
│   ├── build_installer.bat       # Batch wrapper
│   ├── build.ps1                 # Simple build script
│   ├── deadlink_gui.spec         # PyInstaller config
│   ├── installer_script.iss      # Inno Setup config
│   ├── version_info.txt          # Version metadata
│   └── requirements.txt          # Python dependencies
│
├── assets/                       # Assets & Resources
│   ├── sc.png                    # Screenshot
│   ├── run_gui.bat               # Quick launcher
│   └── icon.ico                  # App icon (optional)
│
├── reports/                      # Generated Reports
│   └── .gitkeep                  # Keep directory in git
│
├── dist/                         # Built Executables (generated)
│   └── DeadLinkChecker_v2.0.exe
│
├── build/                        # Build artifacts (generated)
│   └── ...
│
├── installer_output/             # Installers (generated)
│   └── DeadLinkChecker_Setup_v2.0.exe
│
├── .git/                         # Git repository
├── .gitignore                    # Git ignore rules
└── restructure.ps1               # This restructuring script
```

## 📂 Directory Descriptions

### `src/` - Source Code
Contains all Python source code files.
- **deadlink_checker.py**: Core functionality for checking links
- **deadlink_gui.py**: GUI application using CustomTkinter

### `docs/` - Documentation
All documentation files organized in one place.
- User guides (README, QUICKSTART)
- Developer guides (BUILD_INSTALLER, BUILD_REFERENCE)
- License and legal information

### `build_tools/` - Build Configuration
Everything needed to build the application.
- Build scripts (PowerShell, Batch)
- PyInstaller configuration
- Inno Setup installer script
- Version information
- Python dependencies list

### `assets/` - Assets & Resources
Images, icons, and other resources.
- Screenshots for documentation
- Application icons
- Quick launcher scripts

### `reports/` - Generated Reports
Output directory for link check reports.
- TXT reports
- PDF reports
- CSV reports

### `dist/` - Distribution (Generated)
Built executables ready for distribution.
- Created by PyInstaller
- Contains standalone .exe files

### `build/` - Build Artifacts (Generated)
Temporary build files.
- Created by PyInstaller
- Can be safely deleted

### `installer_output/` - Installers (Generated)
Windows installer files.
- Created by Inno Setup
- Ready for distribution

## 🔄 How to Restructure

### Option 1: Automatic (Recommended)
Run the restructuring script:
```powershell
.\restructure.ps1
```

This will:
1. Create new directory structure
2. Move all files to appropriate locations
3. Update file references automatically

### Option 2: Manual
1. Create directories: `src`, `docs`, `build_tools`, `assets`
2. Move files according to structure above
3. Update file paths in:
   - `build_tools/build_installer.ps1`
   - `build_tools/deadlink_gui.spec`
   - `build_tools/installer_script.iss`

## 🚀 Building After Restructure

### From Project Root:
```powershell
cd build_tools
.\build_installer.ps1
```

### Or use the batch file:
```powershell
cd build_tools
.\build_installer.bat
```

## 📝 File Path Updates

After restructuring, these paths change:

### In `deadlink_gui.spec`:
```python
# Before
['deadlink_gui.py']

# After
['../src/deadlink_gui.py']
```

### In `installer_script.iss`:
```ini
; Before
Source: "dist\DeadLinkChecker_v2.0.exe"
Source: "README.md"

; After
Source: "../dist/DeadLinkChecker_v2.0.exe"
Source: "../docs/README.md"
```

### In `build_installer.ps1`:
```powershell
# Before
pip install -r requirements.txt

# After (no change, script handles paths)
pip install -r requirements.txt
```

## 🎯 Benefits of New Structure

### ✅ Organization
- Clear separation of concerns
- Easy to find files
- Professional project layout

### ✅ Maintainability
- Source code isolated from build tools
- Documentation centralized
- Build artifacts separated

### ✅ Scalability
- Easy to add new source files
- Easy to add new documentation
- Easy to add new build configurations

### ✅ Collaboration
- Standard project structure
- Clear file organization
- Easy for new developers to understand

## 📦 .gitignore Updates

After restructuring, update `.gitignore`:
```gitignore
# Build artifacts
build/
dist/
installer_output/

# Python cache
__pycache__/
*.pyc
*.pyo

# Reports (optional - keep if you want to track reports)
reports/*.txt
reports/*.pdf
reports/*.csv
!reports/.gitkeep

# IDE
.vscode/
.idea/
*.code-workspace
```

## 🔧 Development Workflow

### 1. Edit Source Code
```
src/deadlink_checker.py
src/deadlink_gui.py
```

### 2. Test Locally
```powershell
python src/deadlink_gui.py
```

### 3. Update Documentation
```
docs/README.md
docs/QUICKSTART.md
```

### 4. Build Executable
```powershell
cd build_tools
.\build_installer.ps1
```

### 5. Distribute
```
dist/DeadLinkChecker_v2.0.exe
installer_output/DeadLinkChecker_Setup_v2.0.exe
```

## 📚 Quick Reference

| Task | Command |
|------|---------|
| Restructure project | `.\restructure.ps1` |
| Build executable | `cd build_tools && .\build_installer.ps1` |
| Run from source | `python src\deadlink_gui.py` |
| View docs | Open `docs\README.md` |
| Check reports | Open `reports\` folder |

## ⚠️ Important Notes

1. **Run restructure script only once**
   - It moves files, not copies
   - Backup first if unsure

2. **Build from build_tools directory**
   - Scripts use relative paths
   - Must be in correct directory

3. **Don't commit build artifacts**
   - dist/, build/, installer_output/
   - Add to .gitignore

4. **Keep reports/ structure**
   - Used by application
   - .gitkeep ensures directory exists

## 🆘 Troubleshooting

### "File not found" errors
- Ensure you're in the correct directory
- Check file paths in build scripts
- Run restructure script again if needed

### Build fails after restructure
- Check `deadlink_gui.spec` paths
- Check `installer_script.iss` paths
- Ensure all files moved correctly

### Can't find executable
- Check `dist/` directory
- Look for `DeadLinkChecker_v2.0.exe`
- Check build script output for errors

---

**Clean, organized, professional structure!** 🎉
