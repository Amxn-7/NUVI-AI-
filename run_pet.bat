@echo off
setlocal
cd /d "%~dp0"

if not exist "dist\DesktopPetAssistant\DesktopPetAssistant.exe" (
  echo DesktopPetAssistant.exe was not found.
  echo Run build_exe.bat first.
  exit /b 1
)

start "" "%~dp0dist\DesktopPetAssistant\DesktopPetAssistant.exe"
