# Build Script for Dead Link Checker Desktop Application
# This script builds a standalone Windows executable

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dead Link Checker - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller not found. Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host ""

# Clean previous builds
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Build the executable
pyinstaller --clean deadlink_gui.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\DeadLinkChecker.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now distribute the DeadLinkChecker.exe file" -ForegroundColor Cyan
    Write-Host "as a standalone application!" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Build failed! Please check the errors above." -ForegroundColor Red
    Write-Host ""
}

# Pause to see results
Read-Host "Press Enter to exit"
