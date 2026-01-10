# Dead Link Checker - Directory Restructuring Script
# This script organizes all project files into a clean, professional structure

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dead Link Checker - Restructuring" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define new directory structure
$directories = @(
    "src",                    # Source code
    "docs",                   # Documentation
    "build_tools",            # Build scripts and configs
    "assets",                 # Images, icons, etc.
    "reports"                 # Reports output (keep existing)
)

# Create directories
Write-Host "Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[OK] Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] Already exists: $dir" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Moving files to new structure..." -ForegroundColor Yellow

# Move source code files
$sourceFiles = @(
    "deadlink_checker.py",
    "deadlink_gui.py"
)

foreach ($file in $sourceFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "src\" -Force
        Write-Host "[OK] Moved: $file -> src\" -ForegroundColor Green
    }
}

# Move documentation files
$docFiles = @(
    "README.md",
    "QUICKSTART.md",
    "LICENSE.txt",
    "BUILD_INSTALLER.md",
    "BUILD_REFERENCE.txt",
    "BUILD_FIXES.md",
    "INSTALLATION_GUIDE.md",
    "INSTALLER_SETUP_SUMMARY.md",
    "VERSIONED_FILENAME.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "docs\" -Force
        Write-Host "[OK] Moved: $file -> docs\" -ForegroundColor Green
    }
}

# Move build tools
$buildFiles = @(
    "build.ps1",
    "build_installer.ps1",
    "build_installer.bat",
    "deadlink_gui.spec",
    "installer_script.iss",
    "version_info.txt",
    "requirements.txt"
)

foreach ($file in $buildFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "build_tools\" -Force
        Write-Host "[OK] Moved: $file -> build_tools\" -ForegroundColor Green
    }
}

# Move assets
$assetFiles = @(
    "sc.png",
    "run_gui.bat"
)

foreach ($file in $assetFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "assets\" -Force
        Write-Host "[OK] Moved: $file -> assets\" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Updating file references..." -ForegroundColor Yellow

# Update build_installer.ps1 to reference new paths
$buildScriptPath = "build_tools\build_installer.ps1"
if (Test-Path $buildScriptPath) {
    $content = Get-Content $buildScriptPath -Raw
    $content = $content -replace 'requirements\.txt', '..\build_tools\requirements.txt'
    $content = $content -replace 'deadlink_gui\.spec', 'deadlink_gui.spec'
    $content = $content -replace 'installer_script\.iss', 'installer_script.iss'
    Set-Content -Path $buildScriptPath -Value $content
    Write-Host "[OK] Updated: build_installer.ps1" -ForegroundColor Green
}

# Update deadlink_gui.spec to reference new paths
$specPath = "build_tools\deadlink_gui.spec"
if (Test-Path $specPath) {
    $content = Get-Content $specPath -Raw
    $content = $content -replace "\['deadlink_gui\.py'\]", "['../src/deadlink_gui.py']"
    $content = $content -replace "version='version_info\.txt'", "version='version_info.txt'"
    Set-Content -Path $specPath -Value $content
    Write-Host "[OK] Updated: deadlink_gui.spec" -ForegroundColor Green
}

# Update installer_script.iss to reference new paths
$issPath = "build_tools\installer_script.iss"
if (Test-Path $issPath) {
    $content = Get-Content $issPath -Raw
    $content = $content -replace 'Source: "dist\\', 'Source: "../dist\'
    $content = $content -replace 'Source: "README\.md"', 'Source: "../docs/README.md"'
    $content = $content -replace 'Source: "QUICKSTART\.md"', 'Source: "../docs/QUICKSTART.md"'
    $content = $content -replace 'Source: "reports\\', 'Source: "../reports\'
    $content = $content -replace 'LicenseFile=LICENSE\.txt', 'LicenseFile=..\docs\LICENSE.txt'
    Set-Content -Path $issPath -Value $content
    Write-Host "[OK] Updated: installer_script.iss" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "[SUCCESS] Restructuring Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "New directory structure:" -ForegroundColor Cyan
Write-Host "  src/           - Source code" -ForegroundColor Gray
Write-Host "  docs/          - Documentation" -ForegroundColor Gray
Write-Host "  build_tools/   - Build scripts & configs" -ForegroundColor Gray
Write-Host "  assets/        - Images, icons, etc." -ForegroundColor Gray
Write-Host "  reports/       - Generated reports" -ForegroundColor Gray
Write-Host ""
Write-Host "To build, run from project root:" -ForegroundColor Yellow
Write-Host "  cd build_tools" -ForegroundColor Cyan
Write-Host "  .\build_installer.ps1" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
