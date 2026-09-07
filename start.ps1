# PowerShell script to launch Desktop AI Assistant
Set-Location -Path $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "         Starting Desktop AI Assistant" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "$PSScriptRoot\venv\Scripts\python.exe")) {
    Write-Host "[Setup] Virtual environment not found. Creating venv..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[Error] Python is not installed or not in PATH."
        return
    }
    Write-Host "[Setup] Installing dependencies..." -ForegroundColor Yellow
    & "$PSScriptRoot\venv\Scripts\pip.exe" install -r requirements.txt
}

# Load .env variables if present
if (Test-Path "$PSScriptRoot\.env") {
    Write-Host "[Config] Loading variables from .env..." -ForegroundColor Yellow
    Get-Content "$PSScriptRoot\.env" | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $key, $val = $line -split '=', 2
            [System.Environment]::SetEnvironmentVariable($key.Trim(), $val.Trim(), [System.EnvironmentVariableTarget]::Process)
        }
    }
}

# Launch Python process in background
Write-Host "[Launch] Starting Desktop Pet Assistant in background..." -ForegroundColor Green
Start-Process -FilePath "$PSScriptRoot\venv\Scripts\pythonw.exe" -ArgumentList "`"$PSScriptRoot\main.py`"" -WindowStyle Hidden

Write-Host "[Success] Desktop AI Assistant is running!" -ForegroundColor Green
Write-Host "[Info] Look for the pet widget on your screen (bottom-right)." -ForegroundColor Cyan
Write-Host "[Info] Run .\stop.ps1 or stop.bat anytime to close the assistant." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
