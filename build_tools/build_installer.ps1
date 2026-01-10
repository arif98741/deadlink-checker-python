# Complete Build Script for Dead Link Checker
# This script builds the executable and creates a Windows installer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dead Link Checker - Complete Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 0: Auto-increment version
Write-Host "Step 0: Incrementing version number..." -ForegroundColor Yellow
$version = & ".\version_manager.ps1"
if (-not $version) {
    Write-Host "[ERROR] Version increment failed!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] New Version: $version" -ForegroundColor Green
Write-Host ""

# Step 1: Check dependencies
Write-Host "Step 1: Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller not found. Installing dependencies..." -ForegroundColor Yellow
        pip install -r ..\build_tools\requirements.txt
    } else {
        Write-Host "[OK] All Python dependencies are installed" -ForegroundColor Green
    }
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r ..\build_tools\requirements.txt
}

Write-Host ""

# Step 2: Clean previous builds
Write-Host "Step 2: Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "[OK] Removed build directory" -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "[OK] Removed dist directory" -ForegroundColor Green
}
# Clean the actual installer output directory in the parent folder
$parentInstallerDir = Join-Path (Split-Path -Parent $PSScriptRoot) "installer_output"
if (Test-Path $parentInstallerDir) {
    Remove-Item -Recurse -Force $parentInstallerDir
    Write-Host "[OK] Removed installer_output directory" -ForegroundColor Green
}

Write-Host ""

# Step 3: Build the executable
Write-Host "Step 3: Building executable with PyInstaller..." -ForegroundColor Yellow
pyinstaller --clean deadlink_gui.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Executable build failed! Please check the errors above." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Executable built successfully!" -ForegroundColor Green
Write-Host ""

# Step 4: Check if Inno Setup is installed
Write-Host "Step 4: Checking for Inno Setup..." -ForegroundColor Yellow

# Search for Inno Setup in multiple locations
$possiblePaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "C:\Program Files\Inno Setup 5\ISCC.exe",
    "D:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "D:\Program Files\Inno Setup 6\ISCC.exe",
    "D:\Inno Setup 6\ISCC.exe",
    "D:\Inno Setup\ISCC.exe",
    "D:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    "D:\Program Files\Inno Setup 5\ISCC.exe"
)

$iscc = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $iscc = $path
        $version = if ($path -match "Inno Setup 6") { "6" } else { "5" }
        Write-Host "[OK] Found Inno Setup $version at: $path" -ForegroundColor Green
        break
    }
}

if (-not $iscc) {
    Write-Host ""
    Write-Host "[WARNING] Inno Setup not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Searched in:" -ForegroundColor Cyan
    foreach ($path in $possiblePaths) {
        Write-Host "  - $path" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "To create the installer, please:" -ForegroundColor Cyan
    Write-Host "1. Download Inno Setup from: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host "2. Install it to one of the above locations" -ForegroundColor Cyan
    Write-Host "3. Or manually run: ISCC.exe installer_script.iss" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "For now, you can use the executable at: dist\DeadLinkChecker_v$version.exe" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""

# Step 5: Build the installer
Write-Host "Step 5: Building Windows installer..." -ForegroundColor Yellow
& $iscc "installer_script.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "[SUCCESS] BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    $distDir = "dist"
    $installerDir = Join-Path (Split-Path -Parent $PSScriptRoot) "installer_output"
    $exePath = Join-Path $distDir "DeadLinkChecker_v$version.exe"
    $installerPath = Join-Path $installerDir "DeadLinkChecker_Setup_v${version}_x64.exe"
    
    Write-Host "Executable: $exePath" -ForegroundColor Cyan
    Write-Host "Installer:  $installerPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now distribute the installer file!" -ForegroundColor Green
    Write-Host ""
    
    # Show file sizes
    if (Test-Path $exePath) {
        $exeSize = (Get-Item $exePath).Length / 1MB
        Write-Host "Executable size: $([math]::Round($exeSize, 2)) MB" -ForegroundColor Gray
    }
    if (Test-Path $installerPath) {
        $installerSize = (Get-Item $installerPath).Length / 1MB
        Write-Host "Installer size:  $([math]::Round($installerSize, 2)) MB" -ForegroundColor Gray
    }
    Write-Host ""
    
} else {
    Write-Host ""
    Write-Host "[ERROR] Installer build failed! Please check the errors above." -ForegroundColor Red
    Write-Host ""
}

# Pause to see results
Read-Host "Press Enter to exit"

