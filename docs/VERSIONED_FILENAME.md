# Versioned Filename Update

## Changes Made

The executable filename now includes the version number for better version tracking and distribution.

### Before:
```
dist\DeadLinkChecker.exe
```

### After:
```
dist\DeadLinkChecker_v2.0.exe
```

## Files Updated

1. **deadlink_gui.spec**
   - Changed: `name='DeadLinkChecker'` → `name='DeadLinkChecker_v2.0'`
   - Output: `DeadLinkChecker_v2.0.exe`

2. **build_installer.ps1**
   - Updated all references to use `DeadLinkChecker_v2.0.exe`
   - Shows correct filename in success messages

3. **installer_script.iss**
   - Source: `DeadLinkChecker_v2.0.exe` (versioned)
   - Installs as: `DeadLinkChecker.exe` (clean name for shortcuts)
   - **Why**: Users get clean shortcuts without version numbers

## Build Output

After running `.\build_installer.ps1`, you'll get:

### Standalone Executable:
```
📁 dist\
   └── DeadLinkChecker_v2.0.exe  (~60-80 MB)
```

**Distribute this for portable use**
- Filename clearly shows version
- Easy to manage multiple versions
- Users know what version they have

### Installer:
```
📁 installer_output\
   └── DeadLinkChecker_Setup_v2.0.exe  (~65-85 MB)
```

**Distribute this for installation**
- Installs as `DeadLinkChecker.exe` (no version in installed name)
- Shortcuts show clean name: "Dead Link Checker"
- Version info embedded in exe properties

## Why This Approach?

### Distribution Files (Versioned):
✅ `DeadLinkChecker_v2.0.exe` - Clear version tracking
✅ `DeadLinkChecker_Setup_v2.0.exe` - Clear installer version

### Installed Files (Clean):
✅ `C:\Program Files\DeadLinkChecker\DeadLinkChecker.exe`
✅ Start Menu: "Dead Link Checker" (not "Dead Link Checker v2.0")
✅ Desktop: "Dead Link Checker" (clean shortcut name)

## Benefits

1. **Version Tracking**: Easy to identify which version you're distributing
2. **Multiple Versions**: Can keep v1.0, v2.0, v3.0 in same folder
3. **Clean Installation**: Users see clean names in shortcuts
4. **Professional**: Shows version management best practices

## Version Information

The executable still has full version info embedded:
- **Filename**: `DeadLinkChecker_v2.0.exe`
- **File Properties**: Version 2.0.0.0
- **Product Name**: Dead Link Checker
- **Copyright**: © 2026 arif98741

## For Future Versions

When releasing v2.1, v3.0, etc., just update:

1. **deadlink_gui.spec**:
   ```python
   name='DeadLinkChecker_v3.0',  # Update version here
   ```

2. **version_info.txt**:
   ```python
   filevers=(3, 0, 0, 0),  # Update version numbers
   prodvers=(3, 0, 0, 0),
   ```

3. **installer_script.iss**:
   ```ini
   AppVersion=3.0
   OutputBaseFilename=DeadLinkChecker_Setup_v3.0
   Source: "dist\DeadLinkChecker_v3.0.exe"
   ```

Then rebuild!

## Summary

✅ Executable filename includes version: `DeadLinkChecker_v2.0.exe`
✅ Installer filename includes version: `DeadLinkChecker_Setup_v2.0.exe`
✅ Installed app has clean name: `DeadLinkChecker.exe`
✅ Shortcuts have clean name: "Dead Link Checker"
✅ Version info embedded in exe properties
✅ Easy to manage multiple versions

---

**Ready to build with versioned filenames!** 🎉

Run: `.\build_installer.ps1`
