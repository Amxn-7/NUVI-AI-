@echo off
cd /d "%~dp0"

echo ========================================================
echo         Stopping Desktop AI Assistant
echo ========================================================

set "stopped=0"

:: 1. Terminate PyInstaller executable if running
taskkill /F /IM DesktopPetAssistant.exe >nul 2>&1
if not errorlevel 1 set "stopped=1"

:: 2. Terminate python process running main.py
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*main.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1

echo [Success] Desktop AI Assistant has been stopped.
echo ========================================================
timeout /t 2 >nul
