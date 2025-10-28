@echo off
echo Starting SmartFixer Application...
echo.

REM Activate virtual environment and run the application
call venv\Scripts\activate.bat && python main.py

echo.
echo Application stopped.
pause