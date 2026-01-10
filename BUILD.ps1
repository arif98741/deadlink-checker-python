# Dead Link Checker - Build Launcher
# Run this from the project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dead Link Checker - Build Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to build_tools directory
$buildToolsDir = Join-Path $PSScriptRoot "build_tools"

if (Test-Path $buildToolsDir) {
    Write-Host "Navigating to build_tools directory..." -ForegroundColor Yellow
    Set-Location $buildToolsDir
    
    Write-Host "Running build script..." -ForegroundColor Yellow
    Write-Host ""
    
    # Run the build script
    & ".\build_installer.ps1"
} else {
    Write-Host "[ERROR] build_tools directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
