@echo off
echo Opening download pages for required tools...

echo Opening Java JDK Download...
start https://www.oracle.com/java/technologies/downloads/#jdk21-windows

echo Opening GCC (MSYS2) Download...
start https://www.msys2.org/

echo Opening Node.js Download...
start https://nodejs.org/en/download/

echo Opening Go Download...
start https://go.dev/dl/

echo Opening Rust Download...
start https://www.rust-lang.org/tools/install

echo Opening PHP Download...
start https://windows.php.net/download/

echo Opening Ruby Download...
start https://rubyinstaller.org/downloads/

echo.
echo ========================================================
echo All download pages have been opened in your browser.
echo Please download and install them manually.
echo IMPORTANT: Remember to check "Add to PATH" during installation!
echo Refer to setup_guide.md for detailed instructions.
echo ========================================================
pause
