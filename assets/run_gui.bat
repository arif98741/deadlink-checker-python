@echo off
title Dead Link Checker - Desktop Application
echo.
echo ========================================
echo   Dead Link Checker - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run the GUI application
python deadlink_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the application
    echo Please check if all dependencies are installed
    echo Run: pip install -r requirements.txt
    pause
)
