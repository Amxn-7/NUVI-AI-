# PowerShell script to stop Desktop AI Assistant
Set-Location -Path $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "         Stopping Desktop AI Assistant" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Terminate DesktopPetAssistant.exe if running
Get-Process -Name "DesktopPetAssistant" -ErrorAction SilentlyContinue | Stop-Process -Force

# Terminate Python processes running main.py
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*main.py*" } | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host "[Success] Desktop AI Assistant has been stopped." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
