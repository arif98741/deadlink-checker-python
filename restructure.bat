@echo off
echo ========================================
echo Dead Link Checker - Restructure Project
echo ========================================
echo.
echo This will reorganize all project files into a clean structure:
echo   - src/          (Source code)
echo   - docs/         (Documentation)
echo   - build_tools/  (Build scripts)
echo   - assets/       (Images, icons)
echo   - reports/      (Generated reports)
echo.
echo WARNING: This will move files. Make sure you have a backup!
echo.
pause

powershell -ExecutionPolicy Bypass -File "restructure.ps1"

pause
