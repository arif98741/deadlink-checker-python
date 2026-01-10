# 📁 Project Restructuring - Quick Guide

## Current Structure (Messy)
```
deadlink-checker-python/
├── deadlink_checker.py
├── deadlink_gui.py
├── build.ps1
├── build_installer.ps1
├── build_installer.bat
├── deadlink_gui.spec
├── installer_script.iss
├── version_info.txt
├── requirements.txt
├── README.md
├── QUICKSTART.md
├── LICENSE.txt
├── BUILD_INSTALLER.md
├── BUILD_REFERENCE.txt
├── BUILD_FIXES.md
├── INSTALLATION_GUIDE.md
├── INSTALLER_SETUP_SUMMARY.md
├── VERSIONED_FILENAME.md
├── sc.png
├── run_gui.bat
├── reports/
├── build/
└── dist/
```
❌ **Problems:**
- All files mixed together
- Hard to find things
- Unprofessional
- Difficult to maintain

---

## New Structure (Clean & Professional)
```
deadlink-checker-python/
│
├── 📂 src/                       ← SOURCE CODE
│   ├── deadlink_checker.py
│   └── deadlink_gui.py
│
├── 📂 docs/                      ← DOCUMENTATION
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── LICENSE.txt
│   ├── BUILD_INSTALLER.md
│   ├── BUILD_REFERENCE.txt
│   ├── BUILD_FIXES.md
│   ├── INSTALLATION_GUIDE.md
│   ├── INSTALLER_SETUP_SUMMARY.md
│   └── VERSIONED_FILENAME.md
│
├── 📂 build_tools/               ← BUILD SCRIPTS
│   ├── build_installer.ps1
│   ├── build_installer.bat
│   ├── build.ps1
│   ├── deadlink_gui.spec
│   ├── installer_script.iss
│   ├── version_info.txt
│   └── requirements.txt
│
├── 📂 assets/                    ← IMAGES & ICONS
│   ├── sc.png
│   └── run_gui.bat
│
├── 📂 reports/                   ← GENERATED REPORTS
│   └── .gitkeep
│
├── 📂 dist/                      ← BUILT EXECUTABLES
│   └── DeadLinkChecker_v2.0.exe
│
├── 📂 build/                     ← BUILD ARTIFACTS
│   └── (temporary files)
│
└── 📂 installer_output/          ← INSTALLERS
    └── DeadLinkChecker_Setup_v2.0.exe
```
✅ **Benefits:**
- Clean organization
- Easy to navigate
- Professional structure
- Easy to maintain

---

## 🚀 How to Restructure

### Step 1: Run the Script

**Option A: Double-click**
```
restructure.bat
```

**Option B: PowerShell**
```powershell
.\restructure.ps1
```

### Step 2: Verify
Check that files are in correct locations:
- ✅ Source code in `src/`
- ✅ Docs in `docs/`
- ✅ Build tools in `build_tools/`
- ✅ Assets in `assets/`

### Step 3: Build
```powershell
cd build_tools
.\build_installer.ps1
```

---

## 📋 What Gets Moved

### To `src/` (Source Code)
- deadlink_checker.py
- deadlink_gui.py

### To `docs/` (Documentation)
- README.md
- QUICKSTART.md
- LICENSE.txt
- BUILD_INSTALLER.md
- BUILD_REFERENCE.txt
- BUILD_FIXES.md
- INSTALLATION_GUIDE.md
- INSTALLER_SETUP_SUMMARY.md
- VERSIONED_FILENAME.md

### To `build_tools/` (Build Configuration)
- build.ps1
- build_installer.ps1
- build_installer.bat
- deadlink_gui.spec
- installer_script.iss
- version_info.txt
- requirements.txt

### To `assets/` (Resources)
- sc.png
- run_gui.bat

### Stays in Place
- reports/ (already correct)
- dist/ (generated)
- build/ (generated)
- installer_output/ (generated)
- .git/ (version control)
- .gitignore (config)

---

## ⚡ Quick Commands

### Restructure Project
```powershell
.\restructure.bat
```

### Build After Restructure
```powershell
cd build_tools
.\build_installer.ps1
```

### Run from Source
```powershell
python src\deadlink_gui.py
```

### View Documentation
```powershell
start docs\README.md
```

---

## ✅ Checklist

Before restructuring:
- [ ] Backup your project (optional but recommended)
- [ ] Close any open files in editors
- [ ] Commit changes to git (if using)

After restructuring:
- [ ] Verify files are in correct locations
- [ ] Test build process
- [ ] Update any custom scripts you have
- [ ] Update .gitignore if needed

---

## 🎯 File Locations Reference

| File Type | Location |
|-----------|----------|
| Python source | `src/` |
| Documentation | `docs/` |
| Build scripts | `build_tools/` |
| Images/Icons | `assets/` |
| Generated reports | `reports/` |
| Built executables | `dist/` |
| Installers | `installer_output/` |

---

## 🔧 After Restructuring

### To build the project:
1. Open PowerShell
2. Navigate to build_tools: `cd build_tools`
3. Run build script: `.\build_installer.ps1`
4. Find output in `../dist/` and `../installer_output/`

### To run from source:
```powershell
python src\deadlink_gui.py
```

### To view documentation:
Open any file in `docs/` folder

---

## ⚠️ Important Notes

1. **Run restructure script only once**
   - It moves files, doesn't copy them
   - Running twice will cause errors

2. **Build from build_tools directory**
   - Scripts use relative paths
   - Must be in correct directory

3. **Don't manually move files**
   - Use the restructure script
   - It updates file references automatically

---

## 🆘 Need Help?

See detailed documentation:
- `PROJECT_STRUCTURE.md` - Complete structure guide
- `docs/BUILD_INSTALLER.md` - Build instructions
- `docs/BUILD_REFERENCE.txt` - Quick reference

---

**Ready to restructure? Run `restructure.bat`!** 🎉
