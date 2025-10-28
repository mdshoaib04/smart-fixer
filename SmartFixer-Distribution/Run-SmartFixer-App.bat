@echo off
TITLE SmartFixer Application
COLOR 0A
ECHO.
ECHO  ====================================================
ECHO    _____                      _   ______ _          
ECHO   / ____|                    | | |  ____(_)         
ECHO  | (___  _ __ ___  __ _ _ __| |_| |__   _ _ __ ___ 
ECHO   \___ \| '__/ _ \/ _` | '__| __|  __| | | '__/ _ \
ECHO   ____) | | |  __/ (_| | |  | |_| |    | | | |  __/
ECHO  |_____/|_|  \___|\__,_|_|   \__|_|    |_|_|  \___|
ECHO                                                   
ECHO  ====================================================
ECHO.
ECHO  Starting SmartFixer Application...
ECHO.
ECHO  Please wait while we launch SmartFixer in your browser...
ECHO.
ECHO  If your browser doesn't open automatically, please go to:
ECHO  http://localhost:5000
ECHO.
ECHO  To stop the application, close this window.
ECHO.

REM Run the SmartFixer application
dist\SmartFixer-App.exe

ECHO.
ECHO  SmartFixer application has been closed.
ECHO.
pause