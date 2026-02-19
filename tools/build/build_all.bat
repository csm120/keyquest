@echo off
REM build_all.bat (Deprecated)
REM Use tools/build.ps1 as the single entrypoint:
REM   powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target all -Clean
setlocal
pushd "%~dp0\..\.."

echo ========================================
echo KeyQuest Master Builder (Deprecated)
echo ========================================
echo.
echo This script is deprecated.
echo Calling tools/build.ps1...
echo.

powershell -ExecutionPolicy Bypass -File tools/build.ps1 -Target all -Clean
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo Build complete.
pause
popd
