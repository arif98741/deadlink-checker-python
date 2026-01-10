# Complete Build Script for Dead Link Checker
# Run this from the build_tools directory
# This script builds the executable and creates a Windows installer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dead Link Checker - Complete Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the right directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Step 1: Check dependencies
Write-Host "Step 1: Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller not found. Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
    } else {
        Write-Host "[OK] All Python dependencies are installed" -ForegroundColor Green
    }
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""

# Step 2: Clean previous builds
Write-Host "Step 2: Cleaning previous builds..." -ForegroundColor Yellow
$buildDir = Join-Path (Split-Path -Parent $scriptDir) "build"
$distDir = Join-Path (Split-Path -Parent $scriptDir) "dist"
$installerDir = Join-Path (Split-Path -Parent $scriptDir) "installer_output"

if (Test-Path $buildDir) {
    Remove-Item -Recurse -Force $buildDir
    Write-Host "[OK] Removed build directory" -ForegroundColor Green
}
if (Test-Path $distDir) {
    Remove-Item -Recurse -Force $distDir
    Write-Host "[OK] Removed dist directory" -ForegroundColor Green
}
if (Test-Path $installerDir) {
    Remove-Item -Recurse -Force $installerDir
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
$innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$innoSetupPath5 = "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"

if (Test-Path $innoSetupPath) {
    $iscc = $innoSetupPath
    Write-Host "[OK] Found Inno Setup 6" -ForegroundColor Green
} elseif (Test-Path $innoSetupPath5) {
    $iscc = $innoSetupPath5
    Write-Host "[OK] Found Inno Setup 5" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[WARNING] Inno Setup not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To create the installer, please:" -ForegroundColor Cyan
    Write-Host "1. Download Inno Setup from: https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host "2. Install it (use default installation path)" -ForegroundColor Cyan
    Write-Host "3. Run this script again" -ForegroundColor Cyan
    Write-Host ""
    $exePath = Join-Path $distDir "DeadLinkChecker_v2.0.exe"
    Write-Host "For now, you can use the executable at: $exePath" -ForegroundColor Cyan
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
    
    $exePath = Join-Path $distDir "DeadLinkChecker_v2.0.exe"
    $installerPath = Join-Path $installerDir "DeadLinkChecker_Setup_v2.0.exe"
    
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
