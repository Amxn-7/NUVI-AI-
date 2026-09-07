@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================================
echo         Starting Desktop AI Assistant
echo ========================================================

:: Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [Setup] Virtual environment not found. Creating venv...
    python -m venv venv
    if errorlevel 1 (
        echo [Error] Python is not installed or not in PATH. Please install Python.
        pause
        exit /b 1
    )
    echo [Setup] Installing dependencies from requirements.txt...
    "%~dp0venv\Scripts\pip.exe" install -r requirements.txt
    if errorlevel 1 (
        echo [Error] Failed to install requirements.
        pause
        exit /b 1
    )
)

:: Check for .env file
if exist ".env" (
    echo [Config] .env file detected.
)

echo [Launch] Starting Desktop Pet Assistant in background...
start "" "%~dp0venv\Scripts\pythonw.exe" "%~dp0main.py"

echo [Success] Desktop AI Assistant is running!
echo [Info] Look for the pet widget on your screen (bottom-right).
echo [Info] Run "stop.bat" anytime to close the assistant.
echo ========================================================
timeout /t 3 >nul
