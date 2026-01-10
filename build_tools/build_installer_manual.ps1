# Manual Installer Builder
# Use this if Inno Setup is installed in a custom location

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Manual Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ask user for Inno Setup location
Write-Host "Please enter the full path to ISCC.exe" -ForegroundColor Yellow
Write-Host "Example: D:\Inno Setup 6\ISCC.exe" -ForegroundColor Gray
Write-Host ""
$isccPath = Read-Host "ISCC.exe path"

# Validate path
if (-not (Test-Path $isccPath)) {
    Write-Host ""
    Write-Host "[ERROR] File not found: $isccPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the path and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[OK] Found ISCC.exe" -ForegroundColor Green
Write-Host ""

# Build installer
Write-Host "Building installer..." -ForegroundColor Yellow
& $isccPath "installer_script.iss"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Installer built successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installer: ..\installer_output\DeadLinkChecker_Setup_v2.0.exe" -ForegroundColor Cyan
    Write-Host ""
    
    # Show file size
    $installerPath = "..\installer_output\DeadLinkChecker_Setup_v2.0.exe"
    if (Test-Path $installerPath) {
        $installerSize = (Get-Item $installerPath).Length / 1MB
        Write-Host "Installer size: $([math]::Round($installerSize, 2)) MB" -ForegroundColor Gray
    }
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[ERROR] Installer build failed!" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
