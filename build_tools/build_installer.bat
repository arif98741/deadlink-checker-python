@echo off
echo ========================================
echo Dead Link Checker - Build Installer
echo ========================================
echo.
echo This will build the Windows installer.
echo Please wait...
echo.

powershell -ExecutionPolicy Bypass -File "build_installer.ps1"

pause
