@echo off
echo ===================================================
echo      SmartFixer Unified Setup Script
echo ===================================================
echo.

echo [1/2] Installing Python Dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing Python dependencies!
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] Installing System Compilers (Java, GCC, Node, etc.)...
echo This uses Scoop and might take a few minutes.
powershell -ExecutionPolicy Bypass -File install_tools.ps1
if %errorlevel% neq 0 (
    echo Error installing system tools!
    pause
    exit /b %errorlevel%
)

echo.
echo ===================================================
echo      Setup Complete!
echo ===================================================
echo Please restart your terminal/editor now.
pause
