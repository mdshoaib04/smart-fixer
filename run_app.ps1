Write-Host "Starting SmartFixer Application..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment and run the application
& .\venv\Scripts\Activate.ps1
& python main.py

Write-Host ""
Write-Host "Application stopped." -ForegroundColor Yellow